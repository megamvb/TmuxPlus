"""Portuguese (Brazil) translations for TmuxPlus."""

STRINGS: dict[str, str] = {
    # ── App / global ─────────────────────────────────────────────────────────
    "Visual manager for tmux": "Gerenciador visual para tmux",
    "Quit": "Sair",
    "Help": "Ajuda",
    "Theme": "Tema",
    "Theme: {theme}": "Tema: {theme}",

    # ── Command palette ───────────────────────────────────────────────────────
    "Sessions — Manage tmux sessions": "Sessões — Gerenciar sessões tmux",
    "Open sessions screen": "Abrir tela de sessões",
    "Windows — Manage tmux windows": "Janelas — Gerenciar janelas tmux",
    "Open windows screen": "Abrir tela de janelas",
    "Panes — Manage tmux panes": "Painéis — Gerenciar painéis tmux",
    "Open panes screen": "Abrir tela de painéis",
    "Create Session": "Criar Sessão",
    "Create new tmux session": "Criar nova sessão tmux",
    "Help — tmux shortcuts": "Ajuda — Atalhos tmux",
    "Show help": "Exibir ajuda",
    "Toggle Theme": "Alternar Tema",
    "Toggle between themes": "Alternar entre temas",
    "Exit TmuxPlus": "Encerrar TmuxPlus",

    # ── Navigation / action labels ────────────────────────────────────────────
    "Sessions": "Sessões",
    "Windows": "Janelas",
    "Panes": "Painéis",
    "Create": "Criar",
    "Rename": "Renomear",
    "Attach": "Anexar",
    "Kill": "Matar",
    "Save": "Salvar",
    "Load": "Carregar",
    "Back": "Voltar",
    "Refresh": "Atualizar",
    "Select": "Selecionar",
    "Close": "Fechar",
    "Send Cmd": "Enviar Cmd",
    "Split V": "Split V",
    "Split H": "Split H",

    # ── Home screen ───────────────────────────────────────────────────────────
    "Sessions:": "Sessões:",
    "Attached:": "Anexadas:",
    "Windows:": "Janelas:",
    "Saved:": "Salvas:",

    # ── Table column headers ──────────────────────────────────────────────────
    "Name": "Nome",
    "Status": "Status",
    "Type": "Tipo",
    "Index": "Índice",
    "Active": "Ativa",
    "Size": "Tamanho",
    "Command": "Comando",
    "ID": "ID",
    "Path": "Caminho",

    # ── Session status / type values ──────────────────────────────────────────
    "Attached": "Anexada",
    "Detached": "Desanexada",
    "Saved": "Salva",
    "Yes": "Sim",
    "No": "Não",

    # ── Sessions screen ───────────────────────────────────────────────────────
    "Tmux Sessions": "Sessões Tmux",
    "New session name:": "Nome da nova sessão:",
    "my-session": "minha-sessao",
    "Session '{name}' created!": "Sessão '{name}' criada!",
    "Error creating session '{name}'": "Erro ao criar sessão '{name}'",
    "Select a session first": "Selecione uma sessão primeiro",
    "New name for '{name}':": "Novo nome para '{name}':",
    "Session renamed to '{name}'": "Sessão renomeada para '{name}'",
    "Error renaming session": "Erro ao renomear sessão",
    "Press Ctrl+B, D to detach and return to TmuxPlus": "Ctrl+B, D para desanexar e voltar ao TmuxPlus",
    "Session not found": "Sessão não encontrada",
    "Kill session '{name}'?": "Deseja realmente matar a sessão '{name}'?",
    "Session '{name}' terminated": "Sessão '{name}' encerrada",
    "Error terminating session": "Erro ao encerrar sessão",
    "This session is already saved to disk": "Esta sessão já está salva em disco",
    "Session '{name}' saved!": "Sessão '{name}' salva!",
    "Error saving session '{name}'": "Erro ao salvar sessão '{name}'",
    "Select a saved session first": "Selecione uma sessão salva primeiro",
    "This session is already active": "Esta sessão já está ativa",
    "Session '{name}' restored!": "Sessão '{name}' restaurada!",
    "Error restoring session '{name}'": "Erro ao restaurar sessão '{name}'",
    "List refreshed": "Lista atualizada",

    # ── Windows screen ────────────────────────────────────────────────────────
    "Tmux Windows": "Janelas Tmux",
    "Select a session": "Selecione uma sessão",
    "New window name:": "Nome da nova janela:",
    "my-window": "minha-janela",
    "Window '{name}' created!": "Janela '{name}' criada!",
    "Error creating window": "Erro ao criar janela",
    "Select a window first": "Selecione uma janela primeiro",
    "New name for '{name}':": "Novo nome para '{name}':",  # shared with sessions
    "Window renamed to '{name}'": "Janela renomeada para '{name}'",
    "Error renaming window": "Erro ao renomear janela",
    "Window '{name}' selected": "Janela '{name}' selecionada",
    "Error selecting window": "Erro ao selecionar janela",
    "Close window '{name}'?": "Fechar a janela '{name}'?",
    "Window '{name}' closed": "Janela '{name}' fechada",
    "Error closing window": "Erro ao fechar janela",

    # ── Panes screen ──────────────────────────────────────────────────────────
    "Tmux Panes": "Painéis Tmux",
    "Session": "Sessão",
    "Window": "Janela",
    "Select a window first": "Selecione uma janela primeiro",  # shared with windows
    "Vertical split created!": "Split vertical criado!",
    "Error creating split": "Erro ao criar split",
    "Horizontal split created!": "Split horizontal criado!",
    "History": "Histórico",
    "Aliases": "Aliases",
    "Shell Aliases": "Aliases do Shell",
    "Filter aliases...": "Filtrar aliases...",
    "No aliases found": "Nenhum alias encontrado",
    "Command History": "Histórico de Comandos",
    "Filter commands...": "Filtrar comandos...",
    "No commands found": "Nenhum comando encontrado",
    "Select a pane first": "Selecione um painel primeiro",
    "Command to send to pane:": "Comando para enviar ao painel:",
    "Command sent to pane {id}": "Comando enviado ao painel {id}",
    "Error sending command": "Erro ao enviar comando",
    "Close pane '{id}'?": "Fechar o painel '{id}'?",
    "Pane {id} closed": "Painel {id} fechado",
    "Error closing pane": "Erro ao fechar painel",

    # ── Command guard ──────────────────────────────────────────────────────────
    "Command blocked: destructive rm on root is not allowed":
        "Comando bloqueado: rm destrutivo na raiz não é permitido",
    "Dangerous command: '{cmd}'\nAre you sure you want to send it?":
        "Comando perigoso: '{cmd}'\nTem certeza que deseja enviá-lo?",

    # ── Help modal ────────────────────────────────────────────────────────────
    "Help — Tmux Commands": "Ajuda — Comandos Tmux",
    "Close": "Fechar",
    "TMUX_HELP_TEXT": """\
[bold cyan]═══ Comandos TmuxPlus ═══[/]

[bold green]── Global ───────────────────────────────────────[/]
[bold]Ctrl+Q[/]          Sair do TmuxPlus
[bold]Ctrl+T[/]          Alternar tema
[bold]?[/]               Ajuda
[bold]Ctrl+P[/]          Paleta de comandos

[bold green]── Tela Home ────────────────────────────────────[/]
[bold]1[/]               Sessões
[bold]2[/]               Janelas
[bold]3[/]               Painéis
[bold]q[/]               Sair

[bold green]── Tela Sessões ─────────────────────────────────[/]
[bold]c[/]               Criar sessão
[bold]r[/]               Renomear sessão
[bold]a[/]               Anexar à sessão
[bold]k[/]               Matar sessão
[bold]s[/]               Salvar sessão em disco
[bold]l[/]               Carregar sessão salva
[bold]F5[/]              Atualizar lista
[bold]Escape[/]          Voltar

[bold green]── Tela Janelas ─────────────────────────────────[/]
[bold]c[/]               Criar janela
[bold]r[/]               Renomear janela
[bold]s[/]               Selecionar janela
[bold]k[/]               Fechar janela
[bold]F5[/]              Atualizar lista
[bold]Escape[/]          Voltar

[bold green]── Tela Painéis ─────────────────────────────────[/]
[bold]v[/]               Split vertical
[bold]h[/]               Split horizontal
[bold]x[/]               Enviar comando ao painel
[bold]H[/]               Histórico de comandos
[bold]k[/]               Fechar painel
[bold]F5[/]              Atualizar lista
[bold]Escape[/]          Voltar

[bold green]── Popup Tmux (dentro do terminal) ───────────────[/]
[bold]Ctrl+B  H[/]       Histórico de comandos (popup filtrável)
[bold]Ctrl+B  A[/]       Aliases do shell (popup filtrável)

[bold cyan]═══ Comandos Tmux Essenciais ═══[/]

[bold yellow]Prefixo padrão:[/] [bold white]Ctrl+B[/]  (todos os comandos abaixo usam este prefixo)

[bold green]── Sessões ──────────────────────────────────────[/]
[bold]Ctrl+B  s[/]       Listar sessões
[bold]Ctrl+B  $[/]       Renomear sessão atual
[bold]Ctrl+B  d[/]       Desanexar da sessão
[bold]Ctrl+B  ([/]       Sessão anterior
[bold]Ctrl+B  )[/]       Próxima sessão

[bold green]── Janelas ──────────────────────────────────────[/]
[bold]Ctrl+B  c[/]       Criar nova janela
[bold]Ctrl+B  ,[/]       Renomear janela atual
[bold]Ctrl+B  w[/]       Listar janelas
[bold]Ctrl+B  n[/]       Próxima janela
[bold]Ctrl+B  p[/]       Janela anterior
[bold]Ctrl+B  0-9[/]     Ir para janela pelo número
[bold]Ctrl+B  &[/]       Fechar janela atual

[bold green]── Painéis ──────────────────────────────────────[/]
[bold]Ctrl+B  %[/]       Dividir verticalmente
[bold]Ctrl+B  "[/]       Dividir horizontalmente
[bold]Ctrl+B  ←↑↓→[/]   Navegar entre painéis
[bold]Ctrl+B  x[/]       Fechar painel atual
[bold]Ctrl+B  z[/]       Zoom (maximizar/restaurar) painel
[bold]Ctrl+B  {[/]       Mover painel para esquerda
[bold]Ctrl+B  }[/]       Mover painel para direita
[bold]Ctrl+B  ![/]       Converter painel em janela
[bold]Ctrl+B  Space[/]   Alternar layout dos painéis

[bold green]── Copiar e Colar ───────────────────────────────[/]
[bold]Ctrl+B  [[/]       Entrar no modo de cópia
[bold]Ctrl+B  ][/]       Colar buffer

[bold green]── Redimensionar Painéis ────────────────────────[/]
[bold]Ctrl+B  Ctrl+←↑↓→[/]   Redimensionar painel

[bold green]── Diversos ─────────────────────────────────────[/]
[bold]Ctrl+B  t[/]       Mostrar relógio
[bold]Ctrl+B  ?[/]       Listar todos os atalhos do tmux
[bold]Ctrl+B  :[/]       Prompt de comando tmux
[bold]Ctrl+B  ~[/]       Mostrar mensagens anteriores\
""",

    # ── Modals ────────────────────────────────────────────────────────────────
    "Confirm": "Confirmar",
    "Cancel": "Cancelar",
    "Yes": "Sim",
    "No": "Não",
}
