package main

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"

	"github.com/charmbracelet/bubbles/help"
	"github.com/charmbracelet/bubbles/key"
	"github.com/charmbracelet/bubbles/spinner"
	"github.com/charmbracelet/bubbles/textinput"
	"github.com/charmbracelet/bubbles/viewport"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/glamour"
	"github.com/charmbracelet/lipgloss"
	"github.com/google/uuid"
	"github.com/mattn/go-isatty"
	"gopkg.in/yaml.v3"
)

// --- STYLING ---
var (
	titleStyle   = lipgloss.NewStyle().Foreground(lipgloss.Color("#FFF")).Background(lipgloss.Color("#5A56E0")).Padding(0, 1)
	statusStyle  = lipgloss.NewStyle().Foreground(lipgloss.AdaptiveColor{Light: "#8470FF", Dark: "#7D56F4"})
	helpStyle    = lipgloss.NewStyle().Foreground(lipgloss.Color("#626262")).Italic(true)
	successStyle = lipgloss.NewStyle().Foreground(lipgloss.Color("#32CD32"))
	errorStyle   = lipgloss.NewStyle().Foreground(lipgloss.Color("#FF0000"))
	pendingStyle = lipgloss.NewStyle().Foreground(lipgloss.Color("#AAAAAA"))
)

// --- CONFIGURATION ---
type Config struct {
	Logging       LoggingConfig       `yaml:"logging"`
	OpenTelemetry OpenTelemetryConfig `yaml:"opentelemetry"`
}
type LoggingConfig struct {
	EnableLocalFiles bool   `yaml:"enable_local_files"`
	Directory        string `yaml:"directory"`
}
type OpenTelemetryConfig struct {
	Enabled      bool   `yaml:"enabled"`
	ExporterType string `yaml:"exporter_type"`
	Endpoint     string `yaml:"endpoint"`
}

func loadConfig() (*Config, error) {
	configPath := filepath.Join("..", ".ai-safe-ops", "config.yml")
	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		defaultConfig := getDefaultConfig()
		configDir := filepath.Dir(configPath)
		if err := os.MkdirAll(configDir, 0755); err != nil {
			return nil, err
		}
		data, err := yaml.Marshal(defaultConfig)
		if err != nil {
			return nil, err
		}
		if err := os.WriteFile(configPath, data, 0644); err != nil {
			return nil, err
		}
		return defaultConfig, nil
	}
	data, err := os.ReadFile(configPath)
	if err != nil {
		return nil, err
	}
	var cfg Config
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return nil, err
	}
	return &cfg, nil
}

func getDefaultConfig() *Config {
	return &Config{
		Logging: LoggingConfig{
			EnableLocalFiles: true,
			Directory:        "../.ai-safe-ops/logs",
		},
		OpenTelemetry: OpenTelemetryConfig{
			Enabled:      false,
			ExporterType: "console",
			Endpoint:     "http://localhost:4318/v1/traces",
		},
	}
}

// --- APP STATES & MESSAGES ---
type appState int

const (
	stateMainMenu appState = iota
	stateWorkflowSelection
	stateDirectorySelection
	stateRunningWorkflow
	stateResults
)

type stepStatus int

const (
	statusPending stepStatus = iota
	statusRunning
	statusDone
	statusError
)

type workflowStep struct {
	name   string
	status stepStatus
}

type processOutputMsg struct{ line string }
type processFinishedMsg struct {
	err        error
	reportPath string
}

// --- KEYMAP ---
type keyMap struct {
	Up   key.Binding
	Down key.Binding
	Quit key.Binding
}

func (k keyMap) ShortHelp() []key.Binding {
	return []key.Binding{k.Up, k.Down, k.Quit}
}
func (k keyMap) FullHelp() [][]key.Binding {
	return [][]key.Binding{{k.Up, k.Down, k.Quit}}
}

var keys = keyMap{
	Up:   key.NewBinding(key.WithKeys("k", "up"), key.WithHelp("↑/k", "up")),
	Down: key.NewBinding(key.WithKeys("j", "down"), key.WithHelp("↓/j", "down")),
	Quit: key.NewBinding(key.WithKeys("q", "ctrl+c"), key.WithHelp("q", "quit")),
}

// --- MAIN MODEL ---
type mainMenuModel struct {
	config        *Config
	choices       []string
	cursor        int
	state         appState
	workflow      string
	codebase      string
	spinner       spinner.Model
	steps         []workflowStep
	err           error
	textInput     textinput.Model
	viewport      viewport.Model
	help          help.Model
	keys          keyMap
	ready         bool
	stdoutScanner *bufio.Scanner
}

func initialMainMenuModel(cfg *Config) mainMenuModel {
	ti := textinput.New()
	ti.Placeholder = "/path/to/your/codebase"
	ti.Focus()
	ti.Width = 60
	s := spinner.New()
	s.Spinner = spinner.Dot
	s.Style = statusStyle
	return mainMenuModel{
		config:    cfg,
		choices:   []string{"Start Workflow", "Settings"},
		state:     stateMainMenu,
		spinner:   s,
		textInput: ti,
		help:      help.New(),
		keys:      keys,
	}
}

func (m mainMenuModel) Init() tea.Cmd {
	return textinput.Blink
}

// --- UPDATE LOGIC ---
func (m mainMenuModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var (
		cmd  tea.Cmd
		cmds []tea.Cmd
	)
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		headerHeight := lipgloss.Height(m.headerView())
		footerHeight := lipgloss.Height(m.footerView())
		verticalMargin := headerHeight + footerHeight
		if !m.ready {
			m.viewport = viewport.New(msg.Width, msg.Height-verticalMargin)
			m.viewport.YPosition = headerHeight
			m.help.Width = msg.Width
			m.ready = true
		} else {
			m.viewport.Width = msg.Width
			m.viewport.Height = msg.Height - verticalMargin
			m.help.Width = msg.Width
		}
	case tea.KeyMsg:
		if key.Matches(msg, m.keys.Quit) {
			return m, tea.Quit
		}
		switch m.state {
		case stateMainMenu, stateWorkflowSelection:
			return m.updateMenus(msg)
		case stateDirectorySelection:
			return m.updateDirectoryInput(msg)
		case stateResults:
			m.viewport, cmd = m.viewport.Update(msg)
			cmds = append(cmds, cmd)
		}
	case spinner.TickMsg:
		if m.state == stateRunningWorkflow {
			m.spinner, cmd = m.spinner.Update(msg)
			cmds = append(cmds, cmd)
		}
	case processOutputMsg:
		line := msg.line
		if strings.HasPrefix(line, "ALL_STEPS:") {
			steps := strings.Split(strings.TrimPrefix(line, "ALL_STEPS:"), ",")
			m.steps = []workflowStep{}
			for _, stepName := range steps {
				m.steps = append(m.steps, workflowStep{name: stepName, status: statusPending})
			}
		} else if strings.HasPrefix(line, "STEP_START:") {
			stepName := strings.TrimPrefix(line, "STEP_START:")
			for i := range m.steps {
				if m.steps[i].name == stepName {
					m.steps[i].status = statusRunning
				}
			}
		} else if strings.HasPrefix(line, "STEP_DONE:") {
			stepName := strings.TrimPrefix(line, "STEP_DONE:")
			for i := range m.steps {
				if m.steps[i].name == stepName {
					m.steps[i].status = statusDone
				}
			}
		}
		cmds = append(cmds, streamOutput(m.stdoutScanner))
	case processFinishedMsg:
		m.state = stateResults
		m.err = msg.err
		if msg.err == nil && msg.reportPath != "" {
			content, err := os.ReadFile(msg.reportPath)
			if err != nil {
				m.err = err
			} else {
				renderer, _ := glamour.NewTermRenderer(glamour.WithAutoStyle(), glamour.WithWordWrap(m.viewport.Width))
				str, _ := renderer.Render(string(content))
				m.viewport.SetContent(str)
			}
		}
	}
	return m, tea.Batch(cmds...)
}

func (m mainMenuModel) updateMenus(msg tea.KeyMsg) (tea.Model, tea.Cmd) {
	switch msg.String() {
	case "up", "k":
		if m.cursor > 0 {
			m.cursor--
		}
	case "down", "j":
		if m.cursor < len(m.choices)-1 {
			m.cursor++
		}
	case "enter":
		if m.state == stateMainMenu {
			if m.cursor == 0 {
				m.state = stateWorkflowSelection
				m.choices = loadWorkflows()
				m.cursor = 0
			}
		} else {
			m.workflow = strings.TrimSuffix(m.choices[m.cursor], filepath.Ext(m.choices[m.cursor]))
			m.state = stateDirectorySelection
			return m, m.textInput.Focus()
		}
	}
	return m, nil
}

func (m mainMenuModel) updateDirectoryInput(msg tea.KeyMsg) (tea.Model, tea.Cmd) {
	var cmd tea.Cmd
	if msg.String() == "enter" {
		m.codebase = m.textInput.Value()
		if m.codebase != "" {
			m.state = stateRunningWorkflow
			return m, doScan(&m)
		}
		return m, nil
	}
	m.textInput, cmd = m.textInput.Update(msg)
	return m, cmd
}

// --- VIEW LOGIC ---
func (m mainMenuModel) View() string {
	if !m.ready {
		return "Initializing..."
	}

	switch m.state {
	case stateResults:
		if m.err != nil {
			// Spezielle Ansicht für Fehler
			s := strings.Builder{}
			s.WriteString(titleStyle.Render("AI Safe Ops 360") + "\n\n")
			s.WriteString(errorStyle.Render("Workflow failed!") + "\n\n")
			style := lipgloss.NewStyle().Width(m.viewport.Width).BorderStyle(lipgloss.RoundedBorder()).BorderForeground(lipgloss.Color("205")).Padding(1, 2)
			s.WriteString(style.Render(m.err.Error()))
			s.WriteString("\n\n" + helpStyle.Render("press q to quit"))
			return s.String()
		}
		// Ansicht für erfolgreichen Report mit Scrollen
		return fmt.Sprintf("%s\n%s\n%s", m.headerView(), m.viewport.View(), m.footerView())
	default:
		// Ansicht für alle anderen Zustände (Menü, Eingabe, Laufen)
		s := strings.Builder{}
		s.WriteString(titleStyle.Render("AI Safe Ops 360") + "\n\n")
		switch m.state {
		case stateMainMenu, stateWorkflowSelection:
			title := "What would you like to do?"
			if m.state == stateWorkflowSelection {
				title = "Select a workflow:"
			}
			s.WriteString(title + "\n\n")
			for i, choice := range m.choices {
				s.WriteString(renderChoice(choice, m.cursor == i))
			}
			s.WriteString("\n" + helpStyle.Render("(press q to quit)"))
		case stateDirectorySelection:
			s.WriteString("Enter the absolute path to your codebase:\n")
			s.WriteString(m.textInput.View() + "\n")
			s.WriteString("\n" + helpStyle.Render("(press enter to start, q to quit)"))
		case stateRunningWorkflow:
			s.WriteString(fmt.Sprintf("Analyzing %s...\n\n", m.codebase))
			for _, step := range m.steps {
				var statusIcon string
				var style lipgloss.Style
				switch step.status {
				case statusPending:
					statusIcon, style = "⚪", pendingStyle
				case statusRunning:
					statusIcon, style = m.spinner.View(), statusStyle
				case statusDone:
					statusIcon, style = successStyle.Render("✅"), lipgloss.NewStyle()
				case statusError:
					statusIcon, style = errorStyle.Render("❌"), lipgloss.NewStyle()
				}
				s.WriteString(fmt.Sprintf("%s %s\n", statusIcon, style.Render(step.name)))
			}
		}
		return s.String()
	}
}

func (m mainMenuModel) headerView() string {
	title := titleStyle.Render("AI Safe Ops 360")
	statusText := successStyle.Render("Workflow complete!")
	return fmt.Sprintf("%s\n%s", title, statusText)
}
func (m mainMenuModel) footerView() string {
	return m.help.View(m.keys)
}
func renderChoice(choice string, selected bool) string {
	cursor := " "
	if selected {
		cursor = ">"
	}
	return fmt.Sprintf("%s %s\n", statusStyle.Render(cursor), choice)
}

// --- HELPER FUNCTIONS & COMMANDS ---
// ... (der Rest des Codes bleibt unverändert)
func loadWorkflows() []string {
	workflowDir := filepath.Join("..", "ai-safe-ops", "ai_safe_ops", "workflows")
	files, err := os.ReadDir(workflowDir)
	if err != nil {
		return []string{fmt.Sprintf("Error: %v", err)}
	}
	var workflows []string
	for _, file := range files {
		if !file.IsDir() && strings.HasSuffix(file.Name(), ".json") {
			workflows = append(workflows, file.Name())
		}
	}
	if len(workflows) == 0 {
		return []string{"No workflows found"}
	}
	return workflows
}

func doScan(m *mainMenuModel) tea.Cmd {
	cwd, err := os.Getwd()
	if err != nil {
		return func() tea.Msg { return processFinishedMsg{err: err} }
	}
	projectRoot := filepath.Dir(cwd)
	pythonExecutable := filepath.Join(projectRoot, ".venv", "bin", "python")
	if _, err := os.Stat(pythonExecutable); os.IsNotExist(err) {
		return func() tea.Msg {
			return processFinishedMsg{err: fmt.Errorf("python executable not found at %s. Please run 'python3 -m venv .venv' in the project root directory", pythonExecutable)}
		}
	}
	args := []string{"-m", "ai_safe_ops.main", m.workflow, m.codebase}
	var logDir string
	if m.config.Logging.EnableLocalFiles {
		args = append(args, "--enable-local-logs")
		runID := uuid.New().String()
		timestamp := time.Now().Format("20060102_150405")
		logDir = filepath.Join(projectRoot, ".ai-safe-ops", "logs", m.workflow, fmt.Sprintf("%s_%s", runID, timestamp))
		err := os.MkdirAll(logDir, 0755)
		if err != nil {
			return func() tea.Msg { return processFinishedMsg{err: fmt.Errorf("could not create log directory: %w", err)} }
		}
		args = append(args, "--log-dir", logDir)
	}
	cmd := exec.Command(pythonExecutable, args...)
	cmd.Dir = projectRoot
	stdout, _ := cmd.StdoutPipe()
	stderr, _ := cmd.StderrPipe()
	m.stdoutScanner = bufio.NewScanner(stdout)
	err = cmd.Start()
	if err != nil {
		return func() tea.Msg { return processFinishedMsg{err: err} }
	}
	return tea.Batch(streamOutput(m.stdoutScanner), waitForExit(cmd, stderr, logDir), m.spinner.Tick)
}

func streamOutput(scanner *bufio.Scanner) tea.Cmd {
	return func() tea.Msg {
		if scanner.Scan() {
			return processOutputMsg{line: scanner.Text()}
		}
		return nil
	}
}

func waitForExit(c *exec.Cmd, stderr io.ReadCloser, logDir string) tea.Cmd {
	reportPath := filepath.Join(logDir, "report_file.txt")
	return func() tea.Msg {
		errOutput, _ := io.ReadAll(stderr)
		err := c.Wait()
		if err != nil {
			if len(errOutput) > 0 {
				return processFinishedMsg{err: fmt.Errorf("python script error:\n\n%s", string(errOutput))}
			}
			return processFinishedMsg{err: err}
		}
		return processFinishedMsg{err: nil, reportPath: reportPath}
	}
}

// --- MAIN ---
func main() {
	if !isatty.IsTerminal(os.Stdout.Fd()) {
		fmt.Println("This is an interactive TUI. For scripting, please use arguments.")
		os.Exit(1)
	}
	config, err := loadConfig()
	if err != nil {
		fmt.Printf("Error loading configuration: %v\n", err)
		os.Exit(1)
	}
	p := tea.NewProgram(initialMainMenuModel(config), tea.WithAltScreen())
	if _, err := p.Run(); err != nil {
		fmt.Printf("Error running program: %v\n", err)
		os.Exit(1)
	}
}
