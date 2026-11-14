window.CATALOGO = {
"verified_on": "2026-11-13",
"items": [
{
"name": "xlsx (Excel spreadsheets)",
"url": "https://github.com/anthropics/skills/tree/main/skills/xlsx",
"stars": 194132,
"license": "Apache-2.0 (per-skill LICENSE.txt; repo has no top-level license)",
"last_commit": "2026-11-06",
"maintainer": "Anthropic (official, organization)",
"desc_en": "Creates and edits real Excel files with working formulas, charts and formatting: budgets, job cost sheets, commission trackers.",
"desc_pt": "Cria e edita planilhas Excel de verdade, com fórmulas, gráficos e formatação: orçamentos, custos de obra, controle de comissões.",
"for_whom_en": "Everyone; especially contractors, insurance agents and bookkeepers.",
"for_whom_pt": "Todos; especialmente construtores, corretores de seguro e quem cuida das finanças.",
"install_claude_ai": {
"supported": true,
"notes": "Already built into claude.ai (Anthropic skill): enable in Settings > Capabilities (code execution/file creation on). No upload needed."
},
"install_claude_code": [
"/plugin marketplace add anthropics/skills",
"/plugin install document-skills@anthropic-agent-skills"
],
"requires": "Code execution (built in on claude.ai); LibreOffice optional in Claude Code for formula recalculation",
"safety": {
"rating": "safe",
"notes": "Python scripts are local only (openpyxl/LibreOffice via subprocess for recalculation, XML validation with defusedxml). No network calls, no credentials."
},
"cat": "financas",
"official": true
},
{
"name": "docx (Word documents)",
"url": "https://github.com/anthropics/skills/tree/main/skills/docx",
"stars": 194132,
"license": "Apache-2.0 (per-skill LICENSE.txt; repo has no top-level license)",
"last_commit": "2026-11-06",
"maintainer": "Anthropic (official, organization)",
"desc_en": "Creates and edits Word documents, including tracked changes and comments: contracts, letters, proposals, SOPs.",
"desc_pt": "Cria e edita documentos Word, inclusive com controle de alterações e comentários: contratos, cartas, propostas, procedimentos.",
"for_whom_en": "Everyone; immigration law offices, real estate, builders writing proposals.",
"for_whom_pt": "Todos; escritórios de imigração, imobiliárias, construtores que fazem propostas.",
"install_claude_ai": {
"supported": true,
"notes": "Already built into claude.ai (Anthropic skill): enable in Settings > Capabilities (code execution/file creation on). No upload needed."
},
"install_claude_code": [
"/plugin marketplace add anthropics/skills",
"/plugin install document-skills@anthropic-agent-skills"
],
"requires": "Code execution (built in on claude.ai)",
"safety": {
"rating": "safe",
"notes": "Local scripts only (unpack/pack OOXML, accept changes via LibreOffice). No network, no credentials."
},
"cat": "docs",
"official": true
},
{
"name": "pptx (PowerPoint presentations)",
"url": "https://github.com/anthropics/skills/tree/main/skills/pptx",
"stars": 194132,
"license": "Apache-2.0 (per-skill LICENSE.txt; repo has no top-level license)",
"last_commit": "2026-11-06",
"maintainer": "Anthropic (official, organization)",
"desc_en": "Builds and edits PowerPoint decks: sales pitches, client presentations, training slides.",
"desc_pt": "Monta e edita apresentações PowerPoint: apresentações de vendas, para clientes, treinamentos.",
"for_whom_en": "Agents presenting to clients, owners pitching banks or partners.",
"for_whom_pt": "Corretores que apresentam para clientes, donos que apresentam para bancos ou sócios.",
"install_claude_ai": {
"supported": true,
"notes": "Already built into claude.ai (Anthropic skill): enable in Settings > Capabilities (code execution/file creation on). No upload needed."
},
"install_claude_code": [
"/plugin marketplace add anthropics/skills",
"/plugin install document-skills@anthropic-agent-skills"
],
"requires": "Code execution (built in on claude.ai)",
"safety": {
"rating": "safe",
"notes": "Local scripts only (thumbnail rendering, OOXML validation). No network."
},
"cat": "docs",
"official": true
},
{
"name": "pdf (read, fill, merge PDFs)",
"url": "https://github.com/anthropics/skills/tree/main/skills/pdf",
"stars": 194132,
"license": "Apache-2.0 (per-skill LICENSE.txt; repo has no top-level license)",
"last_commit": "2026-11-06",
"maintainer": "Anthropic (official, organization)",
"desc_en": "Reads, extracts tables from, merges, splits and fills PDF forms: applications, invoices, statements.",
"desc_pt": "Lê, extrai tabelas, junta, separa e preenche formulários em PDF: formulários, faturas, extratos.",
"for_whom_en": "Immigration law (forms), insurance (applications), anyone drowning in PDFs.",
"for_whom_pt": "Imigração (formulários), seguros (propostas), qualquer um com muitos PDFs.",
"install_claude_ai": {
"supported": true,
"notes": "Already built into claude.ai (Anthropic skill): enable in Settings > Capabilities (code execution/file creation on). No upload needed."
},
"install_claude_code": [
"/plugin marketplace add anthropics/skills",
"/plugin install document-skills@anthropic-agent-skills"
],
"requires": "Code execution (built in on claude.ai)",
"safety": {
"rating": "safe",
"notes": "Local Python (pypdf/pdfplumber style) only. No network. Note: double-check filled government forms (e.g., USCIS) manually."
},
"cat": "docs",
"official": true
},
{
"name": "doc-coauthoring",
"url": "https://github.com/anthropics/skills/tree/main/skills/doc-coauthoring",
"stars": 194132,
"license": "Apache-2.0 (per-skill LICENSE.txt; repo has no top-level license)",
"last_commit": "2025-12-04",
"maintainer": "Anthropic (official, organization)",
"desc_en": "Guides you step by step to write a proposal, policy or plan with Claude, then checks it reads well for the real reader.",
"desc_pt": "Guia você passo a passo para escrever uma proposta, política ou plano junto com o Claude e confere se ficou claro para quem vai ler.",
"for_whom_en": "Owners who need a business plan, employee handbook or bid proposal.",
"for_whom_pt": "Donos que precisam de plano de negócio, manual do funcionário ou proposta de concorrência.",
"install_claude_ai": {
"supported": true,
"notes": "Download the skill folder, zip it, then claude.ai Settings > Capabilities > Skills > Upload."
},
"install_claude_code": [
"/plugin marketplace add anthropics/skills",
"/plugin install example-skills@anthropic-agent-skills"
],
"requires": "Nothing extra",
"safety": {
"rating": "safe",
"notes": "Single SKILL.md, instructions only. Last updated Dec 2025 (stable, but older than 6 months). No license field in this skill's folder; repo-level terms apply."
},
"cat": "docs",
"official": true
},
{
"name": "internal-comms",
"url": "https://github.com/anthropics/skills/tree/main/skills/internal-comms",
"stars": 194132,
"license": "Apache-2.0 (per-skill LICENSE.txt; repo has no top-level license)",
"last_commit": "2026-04-20",
"maintainer": "Anthropic (official, organization)",
"desc_en": "Writes team updates, newsletters, FAQs and status reports in a consistent format.",
"desc_pt": "Escreve comunicados para a equipe, newsletters, perguntas frequentes e relatórios de status num formato padrão.",
"for_whom_en": "Businesses with crews or staff: cleaning, construction, restaurants.",
"for_whom_pt": "Empresas com equipe: limpeza, construção, restaurantes.",
"install_claude_ai": {
"supported": true,
"notes": "Download the skill folder, zip it, then claude.ai Settings > Capabilities > Skills > Upload."
},
"install_claude_code": [
"/plugin marketplace add anthropics/skills",
"/plugin install example-skills@anthropic-agent-skills"
],
"requires": "Nothing extra",
"safety": {
"rating": "safe",
"notes": "Markdown templates only, no scripts."
},
"cat": "docs",
"official": true
},
{
"name": "skill-creator",
"url": "https://github.com/anthropics/skills/tree/main/skills/skill-creator",
"stars": 194132,
"license": "Apache-2.0 (per-skill LICENSE.txt; repo has no top-level license)",
"last_commit": "2026-04-20",
"maintainer": "Anthropic (official, organization)",
"desc_en": "Helps you create your own custom skill (e.g., 'how we quote a cleaning job') so Claude follows your process every time.",
"desc_pt": "Ajuda a criar sua própria skill (ex.: 'como fazemos orçamento de limpeza') para o Claude seguir seu processo sempre.",
"for_whom_en": "Any owner who repeats the same task; the key 'next step' skill for the talk.",
"for_whom_pt": "Qualquer dono que repete a mesma tarefa; a skill de 'próximo passo' da palestra.",
"install_claude_ai": {
"supported": true,
"notes": "Built into claude.ai as an Anthropic skill (Settings > Capabilities); can also be uploaded as zip."
},
"install_claude_code": [
"/plugin marketplace add anthropics/skills",
"/plugin install example-skills@anthropic-agent-skills",
"(also: /plugin install skill-creator@claude-plugins-official)"
],
"requires": "Nothing for basic use; eval scripts need Claude Code (they call `claude -p`)",
"safety": {
"rating": "safe",
"notes": "Optional eval scripts run `claude -p` locally via subprocess; the HTML report loads Google Fonts. No data sent to third parties."
},
"cat": "docs",
"official": true
},
{
"name": "frontend-design",
"url": "https://github.com/anthropics/skills/tree/main/skills/frontend-design",
"stars": 194132,
"license": "Apache-2.0 (per-skill LICENSE.txt; repo has no top-level license)",
"last_commit": "2026-09-03",
"maintainer": "Anthropic (official, organization)",
"desc_en": "Makes Claude design good-looking web pages and landing pages instead of generic ones.",
"desc_pt": "Faz o Claude criar páginas e landing pages bonitas, fugindo do visual genérico.",
"for_whom_en": "Tech-curious owners building a simple site or promo page.",
"for_whom_pt": "Donos curiosos por tecnologia que querem montar um site ou página de promoção.",
"install_claude_ai": {
"supported": true,
"notes": "Download the skill folder, zip it, then claude.ai Settings > Capabilities > Skills > Upload."
},
"install_claude_code": [
"/plugin marketplace add anthropics/skills",
"/plugin install example-skills@anthropic-agent-skills",
"(also: /plugin install frontend-design@claude-plugins-official)"
],
"requires": "Nothing extra (works best in Claude Code or with artifacts)",
"safety": {
"rating": "safe",
"notes": "Instructions only, no scripts."
},
"cat": "tech",
"official": true
},
{
"name": "small-business (plugin, 44 skills)",
"url": "https://github.com/anthropics/knowledge-work-plugins/tree/main/small-business",
"stars": 35666,
"license": "Apache-2.0",
"last_commit": "2026-11-12",
"maintainer": "Anthropic (official, organization)",
"desc_en": "Anthropic's plugin for running a small business: cash-flow snapshot, chase unpaid invoices, quotes/proposals, payroll prep, review replies, social posts, tax-season organizer. Asks before sending or paying anything.",
"desc_pt": "Plugin da Anthropic para pequenas empresas: fluxo de caixa, cobrança de faturas, orçamentos/propostas, preparação de folha, respostas a avaliações, posts, organização para impostos. Pede aprovação antes de enviar ou pagar.",
"for_whom_en": "Every audience segment; the #1 pick for this talk.",
"for_whom_pt": "Todos os segmentos do público; a escolha nº 1 para a palestra.",
"install_claude_ai": {
"supported": false,
"notes": "Plugin (skills + connectors). Not a single-skill zip: skills reference shared files. On Claude desktop/Cowork install from claude.com/plugins; skills also work without connectors (paste/CSV/PDF)."
},
"install_claude_code": [
"/plugin marketplace add anthropics/knowledge-work-plugins",
"/plugin install small-business@knowledge-work-plugins",
"Then say: \"get me started\""
],
"requires": "Optional connectors/accounts (QuickBooks, Gusto, Square, Stripe, Gmail, HubSpot, Canva, etc.) via OAuth MCP; no API keys typed into chat",
"safety": {
"rating": "safe-with-notes",
"notes": "All Markdown, no scripts. .mcp.json lists ~35 vendor MCP endpoints (official vendor URLs; only used if you connect them). Has explicit rules: personal data (SSNs etc.) never reproduced, untrusted email/web content treated as data, human approval before money/customer actions. Not tax/legal advice."
},
"cat": "tudo",
"official": true
},
{
"name": "marketing (plugin)",
"url": "https://github.com/anthropics/knowledge-work-plugins/tree/main/marketing",
"stars": 35666,
"license": "Apache-2.0",
"last_commit": "2026-09-21",
"maintainer": "Anthropic (official, organization)",
"desc_en": "Campaign plans, content drafts, email sequences, SEO audits, competitor briefs and performance reports.",
"desc_pt": "Planos de campanha, rascunhos de conteúdo, sequências de e-mail, auditoria de SEO, análise de concorrentes e relatórios.",
"for_whom_en": "Owners doing their own marketing: beauty, food, real estate.",
"for_whom_pt": "Donos que fazem o próprio marketing: beleza, alimentação, imóveis.",
"install_claude_ai": {
"supported": false,
"notes": "Plugin (skills + connectors). Not a single-skill zip: skills reference shared files. On Claude desktop/Cowork install from claude.com/plugins; skills also work without connectors (paste/CSV/PDF)."
},
"install_claude_code": [
"/plugin marketplace add anthropics/knowledge-work-plugins",
"/plugin install marketing@knowledge-work-plugins"
],
"requires": "Optional connectors (Canva, HubSpot, Klaviyo, Ahrefs...)",
"safety": {
"rating": "safe",
"notes": "Markdown only; connectors are official vendor MCP URLs, opt-in."
},
"cat": "marketing",
"official": true
},
{
"name": "sales (plugin)",
"url": "https://github.com/anthropics/knowledge-work-plugins/tree/main/sales",
"stars": 35666,
"license": "Apache-2.0",
"last_commit": "2026-10-21",
"maintainer": "Anthropic (official, organization)",
"desc_en": "Call prep, follow-up drafts, objection handling, pipeline review and daily sales briefing.",
"desc_pt": "Preparação de ligações, follow-ups, respostas a objeções, revisão do funil e resumo diário de vendas.",
"for_whom_en": "Life insurance agents, realtors, financial advisors.",
"for_whom_pt": "Corretores de seguro de vida, corretores de imóveis, consultores financeiros.",
"install_claude_ai": {
"supported": false,
"notes": "Plugin (skills + connectors). Not a single-skill zip: skills reference shared files. On Claude desktop/Cowork install from claude.com/plugins; skills also work without connectors (paste/CSV/PDF)."
},
"install_claude_code": [
"/plugin marketplace add anthropics/knowledge-work-plugins",
"/plugin install sales@knowledge-work-plugins"
],
"requires": "Optional CRM/calendar connectors",
"safety": {
"rating": "safe",
"notes": "Markdown only; opt-in vendor connectors. Many skills assume a CRM; still usable by pasting notes."
},
"cat": "vendas",
"official": true
},
{
"name": "customer-support (plugin)",
"url": "https://github.com/anthropics/knowledge-work-plugins/tree/main/customer-support",
"stars": 35666,
"license": "Apache-2.0",
"last_commit": "2026-09-21",
"maintainer": "Anthropic (official, organization)",
"desc_en": "Drafts replies to customer complaints, triages tickets, writes FAQ/help articles, handles escalations.",
"desc_pt": "Rascunha respostas a reclamações, organiza chamados, escreve FAQs e trata casos difíceis.",
"for_whom_en": "Cleaning, food, beauty and any business answering customers daily.",
"for_whom_pt": "Limpeza, alimentação, beleza e quem atende clientes todo dia.",
"install_claude_ai": {
"supported": false,
"notes": "Plugin (skills + connectors). Not a single-skill zip: skills reference shared files. On Claude desktop/Cowork install from claude.com/plugins; skills also work without connectors (paste/CSV/PDF)."
},
"install_claude_code": [
"/plugin marketplace add anthropics/knowledge-work-plugins",
"/plugin install customer-support@knowledge-work-plugins"
],
"requires": "Optional connectors (Intercom, HubSpot, Gmail)",
"safety": {
"rating": "safe",
"notes": "Markdown only; opt-in vendor connectors."
},
"cat": "vendas",
"official": true
},
{
"name": "legal (plugin)",
"url": "https://github.com/anthropics/knowledge-work-plugins/tree/main/legal",
"stars": 35666,
"license": "Apache-2.0",
"last_commit": "2026-09-21",
"maintainer": "Anthropic (official, organization)",
"desc_en": "Reviews contracts and NDAs, flags risk, prepares meeting briefs and compliance checklists for a lawyer to review.",
"desc_pt": "Revisa contratos e NDAs, aponta riscos, prepara resumos e checklists para revisão do advogado.",
"for_whom_en": "Immigration law offices; owners reviewing leases or vendor contracts.",
"for_whom_pt": "Escritórios de imigração; donos revisando aluguel ou contratos com fornecedores.",
"install_claude_ai": {
"supported": false,
"notes": "Plugin (skills + connectors). Not a single-skill zip: skills reference shared files. On Claude desktop/Cowork install from claude.com/plugins; skills also work without connectors (paste/CSV/PDF)."
},
"install_claude_code": [
"/plugin marketplace add anthropics/knowledge-work-plugins",
"/plugin install legal@knowledge-work-plugins"
],
"requires": "Optional connectors (Box, DocuSign)",
"safety": {
"rating": "safe-with-notes",
"notes": "Markdown only. Not legal advice; written with US in-house legal in mind. Lawyers must keep client data rules (confidentiality) in mind."
},
"cat": "juridico",
"official": true
},
{
"name": "brand-voice (plugin, by Tribe AI)",
"url": "https://github.com/anthropics/knowledge-work-plugins/tree/main/partner-built/brand-voice",
"stars": 35666,
"license": "Apache-2.0",
"last_commit": "2026-06-02",
"maintainer": "Anthropic (official, organization)",
"desc_en": "Learns your brand's voice from your existing texts, writes guidelines and checks new content matches it.",
"desc_pt": "Aprende o tom da sua marca a partir dos seus textos, cria um guia e confere se o conteúdo novo segue esse tom.",
"for_whom_en": "Businesses posting in English and Portuguese that want one consistent voice.",
"for_whom_pt": "Negócios que postam em inglês e português e querem um tom consistente.",
"install_claude_ai": {
"supported": false,
"notes": "Plugin with agents/commands; install on Cowork/desktop or Claude Code."
},
"install_claude_code": [
"/plugin marketplace add anthropics/knowledge-work-plugins",
"/plugin install brand-voice@knowledge-work-plugins"
],
"requires": "Optional connectors (Notion, Google Drive, Box...)",
"safety": {
"rating": "safe",
"notes": "Partner-built (Tribe AI), hosted in Anthropic's repo. Markdown only; settings example file, no scripts."
},
"cat": "marketing",
"official": true
},
{
"name": "intuit-quickbooks (plugin, 10 skills)",
"url": "https://github.com/intuit/quickbooks-claude-plugin/tree/main/skills",
"stars": 1,
"license": "Apache-2.0",
"last_commit": "2026-09-16",
"maintainer": "Intuit (official vendor org; listed in Anthropic marketplaces)",
"desc_en": "Official QuickBooks plugin: business health check, chase overdue invoices, turn an email into an estimate/invoice, payroll cost analysis.",
"desc_pt": "Plugin oficial do QuickBooks: check-up financeiro, cobrança de faturas vencidas, transformar e-mail em orçamento/fatura, custo da folha.",
"for_whom_en": "Any business already on QuickBooks Online.",
"for_whom_pt": "Qualquer negócio que já usa QuickBooks Online.",
"install_claude_ai": {
"supported": false,
"notes": "Needs the QuickBooks connector; enable via Claude connectors/plugins directory rather than zip upload."
},
"install_claude_code": [
"/plugin install intuit-quickbooks@claude-plugins-official",
"(or: /plugin marketplace add anthropics/knowledge-work-plugins; /plugin install intuit-quickbooks@knowledge-work-plugins)"
],
"requires": "QuickBooks Online account (OAuth connector; paid QuickBooks subscription)",
"safety": {
"rating": "safe-with-notes",
"notes": "Official Intuit org, Markdown only, links only to qbo.intuit.com. Low GitHub stars (1) because distribution is via Anthropic's marketplace; repo has no own marketplace.json. Can create drafts in your books: review before sending."
},
"cat": "financas",
"official": false
},
{
"name": "canva (plugin)",
"url": "https://github.com/canva-sdks/canva-skills/tree/main/plugins/canva",
"stars": 162,
"license": "Apache-2.0",
"last_commit": "2026-11-11",
"maintainer": "Canva (official vendor org; listed in Anthropic marketplaces)",
"desc_en": "Official Canva plugin: create and edit designs, resize for each social network, brand-check, bulk-create flyers.",
"desc_pt": "Plugin oficial do Canva: cria e edita designs, redimensiona para cada rede social, confere a marca, cria vários panfletos de uma vez.",
"for_whom_en": "Beauty, food, real estate: anyone making flyers and posts.",
"for_whom_pt": "Beleza, alimentação, imóveis: quem faz panfletos e posts.",
"install_claude_ai": {
"supported": false,
"notes": "Uses the Canva connector; on claude.ai connect Canva under Connectors."
},
"install_claude_code": [
"/plugin install canva@claude-plugins-official",
"(or: /plugin marketplace add canva-sdks/canva-skills; /plugin install canva@canva-skills)"
],
"requires": "Canva account (OAuth connector)",
"safety": {
"rating": "safe",
"notes": "Official Canva org, Markdown only; talks only to mcp.canva.com."
},
"cat": "marketing",
"official": false
},
{
"name": "copywriting",
"url": "https://github.com/coreyhaines31/marketingskills/tree/main/skills/copywriting",
"stars": 60174,
"license": "MIT",
"last_commit": "2026-11-09",
"maintainer": "Corey Haines (individual, known SaaS marketer; ~3.8k GitHub followers)",
"desc_en": "Writes or rewrites website and landing-page copy: headlines, offers, calls to action, with claims you can back up.",
"desc_pt": "Escreve ou reescreve textos de site e landing page: títulos, ofertas, chamadas, sem promessas que você não possa provar.",
"for_whom_en": "Anyone with a website or Google Business page.",
"for_whom_pt": "Quem tem site ou perfil no Google.",
"install_claude_ai": {
"supported": true,
"notes": "Download the skill folder, zip it, then claude.ai Settings > Capabilities > Skills > Upload. Each skill folder can be zipped individually; some reference sibling skills."
},
"install_claude_code": [
"/plugin marketplace add coreyhaines31/marketingskills",
"/plugin install marketing-skills@marketingskills",
"(installs all ~50 marketing skills as one plugin)"
],
"requires": "Nothing extra",
"safety": {
"rating": "safe-with-notes",
"notes": "Markdown only (references + evals). Links to optional third-party tool guides in the repo's tools/ folder (some tools need paid API keys; never required). Examples lean toward software/SaaS; adapt to local services."
},
"cat": "marketing",
"official": false
},
{
"name": "copy-editing",
"url": "https://github.com/coreyhaines31/marketingskills/tree/main/skills/copy-editing",
"stars": 60174,
"license": "MIT",
"last_commit": "2026-11-09",
"maintainer": "Corey Haines (individual, known SaaS marketer; ~3.8k GitHub followers)",
"desc_en": "Tightens and proofreads existing text and removes 'AI-sounding' phrases.",
"desc_pt": "Revisa e enxuga textos prontos e tira frases com 'cara de IA'.",
"for_whom_en": "Non-native English writers polishing emails, ads and pages.",
"for_whom_pt": "Quem escreve em inglês como segunda língua e quer polir e-mails, anúncios e páginas.",
"install_claude_ai": {
"supported": true,
"notes": "Download the skill folder, zip it, then claude.ai Settings > Capabilities > Skills > Upload. Each skill folder can be zipped individually; some reference sibling skills."
},
"install_claude_code": [
"/plugin marketplace add coreyhaines31/marketingskills",
"/plugin install marketing-skills@marketingskills",
"(installs all ~50 marketing skills as one plugin)"
],
"requires": "Nothing extra",
"safety": {
"rating": "safe-with-notes",
"notes": "Markdown only (references + evals). Links to optional third-party tool guides in the repo's tools/ folder (some tools need paid API keys; never required)."
},
"cat": "docs",
"official": false
},
{
"name": "seo-audit",
"url": "https://github.com/coreyhaines31/marketingskills/tree/main/skills/seo-audit",
"stars": 60174,
"license": "MIT",
"last_commit": "2026-11-09",
"maintainer": "Corey Haines (individual, known SaaS marketer; ~3.8k GitHub followers)",
"desc_en": "Diagnoses why your site doesn't show up on Google, including local SEO.",
"desc_pt": "Descobre por que seu site não aparece no Google, inclusive SEO local.",
"for_whom_en": "Local service businesses (cleaning, contractors, beauty).",
"for_whom_pt": "Negócios locais de serviço (limpeza, construção, beleza).",
"install_claude_ai": {
"supported": true,
"notes": "Download the skill folder, zip it, then claude.ai Settings > Capabilities > Skills > Upload. Each skill folder can be zipped individually; some reference sibling skills."
},
"install_claude_code": [
"/plugin marketplace add coreyhaines31/marketingskills",
"/plugin install marketing-skills@marketingskills",
"(installs all ~50 marketing skills as one plugin)"
],
"requires": "Nothing extra",
"safety": {
"rating": "safe-with-notes",
"notes": "Markdown only (references + evals). Links to optional third-party tool guides in the repo's tools/ folder (some tools need paid API keys; never required)."
},
"cat": "marketing",
"official": false
},
{
"name": "ai-seo",
"url": "https://github.com/coreyhaines31/marketingskills/tree/main/skills/ai-seo",
"stars": 60174,
"license": "MIT",
"last_commit": "2026-11-09",
"maintainer": "Corey Haines (individual, known SaaS marketer; ~3.8k GitHub followers)",
"desc_en": "Helps your business get mentioned when people ask ChatGPT, Perplexity or Google AI for a recommendation.",
"desc_pt": "Ajuda seu negócio a ser citado quando alguém pede recomendação ao ChatGPT, Perplexity ou IA do Google.",
"for_whom_en": "Owners who want to be found in AI answers.",
"for_whom_pt": "Donos que querem aparecer nas respostas de IA.",
"install_claude_ai": {
"supported": true,
"notes": "Download the skill folder, zip it, then claude.ai Settings > Capabilities > Skills > Upload. Each skill folder can be zipped individually; some reference sibling skills."
},
"install_claude_code": [
"/plugin marketplace add coreyhaines31/marketingskills",
"/plugin install marketing-skills@marketingskills",
"(installs all ~50 marketing skills as one plugin)"
],
"requires": "Nothing extra",
"safety": {
"rating": "safe-with-notes",
"notes": "Markdown only (references + evals). Links to optional third-party tool guides in the repo's tools/ folder (some tools need paid API keys; never required)."
},
"cat": "marketing",
"official": false
},
{
"name": "social",
"url": "https://github.com/coreyhaines31/marketingskills/tree/main/skills/social",
"stars": 60174,
"license": "MIT",
"last_commit": "2026-11-09",
"maintainer": "Corey Haines (individual, known SaaS marketer; ~3.8k GitHub followers)",
"desc_en": "Plans and writes posts, carousels, short-video scripts and content calendars for Instagram, Facebook, TikTok, LinkedIn.",
"desc_pt": "Planeja e escreve posts, carrosséis, roteiros de vídeo curto e calendário para Instagram, Facebook, TikTok, LinkedIn.",
"for_whom_en": "Beauty, food, real estate, cleaning.",
"for_whom_pt": "Beleza, alimentação, imóveis, limpeza.",
"install_claude_ai": {
"supported": true,
"notes": "Download the skill folder, zip it, then claude.ai Settings > Capabilities > Skills > Upload. Each skill folder can be zipped individually; some reference sibling skills."
},
"install_claude_code": [
"/plugin marketplace add coreyhaines31/marketingskills",
"/plugin install marketing-skills@marketingskills",
"(installs all ~50 marketing skills as one plugin)"
],
"requires": "Nothing extra",
"safety": {
"rating": "safe-with-notes",
"notes": "Markdown only (references + evals). Links to optional third-party tool guides in the repo's tools/ folder (some tools need paid API keys; never required)."
},
"cat": "marketing",
"official": false
},
{
"name": "emails",
"url": "https://github.com/coreyhaines31/marketingskills/tree/main/skills/emails",
"stars": 60174,
"license": "MIT",
"last_commit": "2026-11-09",
"maintainer": "Corey Haines (individual, known SaaS marketer; ~3.8k GitHub followers)",
"desc_en": "Builds automatic email sequences: welcome, follow-up, win-back of old customers.",
"desc_pt": "Monta sequências automáticas de e-mail: boas-vindas, acompanhamento, reconquista de clientes antigos.",
"for_whom_en": "Insurance agents, realtors, any business with a client list.",
"for_whom_pt": "Corretores de seguro, de imóveis, qualquer negócio com lista de clientes.",
"install_claude_ai": {
"supported": true,
"notes": "Download the skill folder, zip it, then claude.ai Settings > Capabilities > Skills > Upload. Each skill folder can be zipped individually; some reference sibling skills."
},
"install_claude_code": [
"/plugin marketplace add coreyhaines31/marketingskills",
"/plugin install marketing-skills@marketingskills",
"(installs all ~50 marketing skills as one plugin)"
],
"requires": "Nothing extra",
"safety": {
"rating": "safe-with-notes",
"notes": "Markdown only (references + evals). Links to optional third-party tool guides in the repo's tools/ folder (some tools need paid API keys; never required)."
},
"cat": "marketing",
"official": false
},
{
"name": "referrals",
"url": "https://github.com/coreyhaines31/marketingskills/tree/main/skills/referrals",
"stars": 60174,
"license": "MIT",
"last_commit": "2026-11-09",
"maintainer": "Corey Haines (individual, known SaaS marketer; ~3.8k GitHub followers)",
"desc_en": "Designs referral programs and review campaigns: what to reward and how to ask for reviews.",
"desc_pt": "Cria programas de indicação e campanhas de avaliações: qual recompensa dar e como pedir avaliações.",
"for_whom_en": "Word-of-mouth businesses: cleaning, contractors, beauty, insurance.",
"for_whom_pt": "Negócios de boca a boca: limpeza, construção, beleza, seguros.",
"install_claude_ai": {
"supported": true,
"notes": "Download the skill folder, zip it, then claude.ai Settings > Capabilities > Skills > Upload. Each skill folder can be zipped individually; some reference sibling skills."
},
"install_claude_code": [
"/plugin marketplace add coreyhaines31/marketingskills",
"/plugin install marketing-skills@marketingskills",
"(installs all ~50 marketing skills as one plugin)"
],
"requires": "Nothing extra",
"safety": {
"rating": "safe-with-notes",
"notes": "Markdown only (references + evals). Links to optional third-party tool guides in the repo's tools/ folder (some tools need paid API keys; never required)."
},
"cat": "marketing",
"official": false
},
{
"name": "marketing-ideas",
"url": "https://github.com/coreyhaines31/marketingskills/tree/main/skills/marketing-ideas",
"stars": 60174,
"license": "MIT",
"last_commit": "2026-11-09",
"maintainer": "Corey Haines (individual, known SaaS marketer; ~3.8k GitHub followers)",
"desc_en": "Suggests low-budget marketing ideas from a library of 139 tactics.",
"desc_pt": "Sugere ideias de marketing de baixo custo a partir de 139 táticas.",
"for_whom_en": "Owners with little time or budget.",
"for_whom_pt": "Donos com pouco tempo ou verba.",
"install_claude_ai": {
"supported": true,
"notes": "Download the skill folder, zip it, then claude.ai Settings > Capabilities > Skills > Upload. Each skill folder can be zipped individually; some reference sibling skills."
},
"install_claude_code": [
"/plugin marketplace add coreyhaines31/marketingskills",
"/plugin install marketing-skills@marketingskills",
"(installs all ~50 marketing skills as one plugin)"
],
"requires": "Nothing extra",
"safety": {
"rating": "safe-with-notes",
"notes": "Markdown only (references + evals). Links to optional third-party tool guides in the repo's tools/ folder (some tools need paid API keys; never required). Examples lean toward software/SaaS; adapt to local services."
},
"cat": "marketing",
"official": false
},
{
"name": "pricing",
"url": "https://github.com/coreyhaines31/marketingskills/tree/main/skills/pricing",
"stars": 60174,
"license": "MIT",
"last_commit": "2026-11-09",
"maintainer": "Corey Haines (individual, known SaaS marketer; ~3.8k GitHub followers)",
"desc_en": "Helps decide what to charge, how to package services in tiers and when to raise prices.",
"desc_pt": "Ajuda a decidir quanto cobrar, montar pacotes de serviço e quando aumentar preço.",
"for_whom_en": "Service businesses setting packages (cleaning plans, beauty memberships).",
"for_whom_pt": "Negócios de serviço montando pacotes (planos de limpeza, assinaturas de beleza).",
"install_claude_ai": {
"supported": true,
"notes": "Download the skill folder, zip it, then claude.ai Settings > Capabilities > Skills > Upload. Each skill folder can be zipped individually; some reference sibling skills."
},
"install_claude_code": [
"/plugin marketplace add coreyhaines31/marketingskills",
"/plugin install marketing-skills@marketingskills",
"(installs all ~50 marketing skills as one plugin)"
],
"requires": "Nothing extra",
"safety": {
"rating": "safe-with-notes",
"notes": "Markdown only (references + evals). Links to optional third-party tool guides in the repo's tools/ folder (some tools need paid API keys; never required). Examples lean toward software/SaaS; adapt to local services."
},
"cat": "vendas",
"official": false
},
{
"name": "lead-research-assistant",
"url": "https://github.com/ComposioHQ/awesome-claude-skills/tree/master/lead-research-assistant",
"stars": 79434,
"license": "None declared (no repo or per-skill license)",
"last_commit": "2025-10-17",
"maintainer": "Composio (company org; community-contributed skills)",
"desc_en": "Finds and ranks potential business customers for your service and suggests how to approach each one.",
"desc_pt": "Encontra e classifica possíveis clientes empresariais para o seu serviço e sugere como abordar cada um.",
"for_whom_en": "B2B services: commercial cleaning, contractors, insurance for businesses.",
"for_whom_pt": "Serviços B2B: limpeza comercial, construção, seguros empresariais.",
"install_claude_ai": {
"supported": true,
"notes": "Download the skill folder, zip it, then claude.ai Settings > Capabilities > Skills > Upload."
},
"install_claude_code": [
"No marketplace.json: copy the folder into ~/.claude/skills/lead-research-assistant/ (Claude Code) or upload zip on claude.ai"
],
"requires": "Web search enabled for best results",
"safety": {
"rating": "safe-with-notes",
"notes": "Last updated Oct 2025 (stale, >12 months); no license declared. Single SKILL.md, instructions only. Uses Claude's own web search; no external APIs. Respect anti-spam rules (CAN-SPAM) when contacting leads."
},
"cat": "vendas",
"official": false
},
{
"name": "meeting-insights-analyzer",
"url": "https://github.com/ComposioHQ/awesome-claude-skills/tree/master/meeting-insights-analyzer",
"stars": 79434,
"license": "None declared (no repo or per-skill license)",
"last_commit": "2025-10-17",
"maintainer": "Composio (company org; community-contributed skills)",
"desc_en": "Reviews your meeting or sales-call transcripts and gives feedback: talking too much, filler words, missed questions.",
"desc_pt": "Analisa transcrições de reuniões ou ligações de venda e dá feedback: falar demais, vícios de linguagem, perguntas que faltaram.",
"for_whom_en": "Insurance and real-estate agents improving sales calls.",
"for_whom_pt": "Corretores de seguro e de imóveis melhorando ligações de venda.",
"install_claude_ai": {
"supported": true,
"notes": "Download the skill folder, zip it, then claude.ai Settings > Capabilities > Skills > Upload."
},
"install_claude_code": [
"No marketplace.json: copy the folder into ~/.claude/skills/meeting-insights-analyzer/ or upload zip on claude.ai"
],
"requires": "Transcript files (e.g., from Zoom/Otter)",
"safety": {
"rating": "safe-with-notes",
"notes": "Last updated Oct 2025 (stale, >12 months); no license declared. Single SKILL.md, instructions only. Get consent before recording calls (Florida is a two-party consent state)."
},
"cat": "docs",
"official": false
},
{
"name": "content-research-writer",
"url": "https://github.com/ComposioHQ/awesome-claude-skills/tree/master/content-research-writer",
"stars": 79434,
"license": "None declared (no repo or per-skill license)",
"last_commit": "2025-10-17",
"maintainer": "Composio (company org; community-contributed skills)",
"desc_en": "Co-writes blog posts and newsletters with research, citations, better hooks and section-by-section feedback.",
"desc_pt": "Escreve junto com você posts de blog e newsletters, com pesquisa, fontes, ganchos melhores e feedback por seção.",
"for_whom_en": "Realtors, financial and immigration professionals publishing content.",
"for_whom_pt": "Corretores, profissionais de finanças e de imigração que publicam conteúdo.",
"install_claude_ai": {
"supported": true,
"notes": "Download the skill folder, zip it, then claude.ai Settings > Capabilities > Skills > Upload."
},
"install_claude_code": [
"No marketplace.json: copy the folder into ~/.claude/skills/content-research-writer/ or upload zip on claude.ai"
],
"requires": "Web search for citations",
"safety": {
"rating": "safe-with-notes",
"notes": "Last updated Oct 2025 (stale, >12 months); no license declared. Single SKILL.md, instructions only."
},
"cat": "docs",
"official": false
},
{
"name": "meetings",
"url": "https://github.com/alirezarezvani/claude-skills/tree/main/productivity/meetings",
"stars": 29769,
"license": "MIT",
"last_commit": "2026-10-30",
"maintainer": "Alireza Rezvani (individual, known maintainer; ~2.9k followers)",
"desc_en": "Decides if a meeting is worth it (shows its dollar cost), builds a tight agenda and turns notes into action items with owner and due date.",
"desc_pt": "Diz se a reunião vale a pena (mostra o custo em dólar), monta pauta enxuta e transforma anotações em tarefas com responsável e prazo.",
"for_whom_en": "Owners with teams or crews; office managers.",
"for_whom_pt": "Donos com equipe; gerentes de escritório.",
"install_claude_ai": {
"supported": true,
"notes": "Download the skill folder, zip it, then claude.ai Settings > Capabilities > Skills > Upload. Zip the inner skills/meetings folder; scripts need code execution enabled."
},
"install_claude_code": [
"/plugin marketplace add alirezarezvani/claude-skills",
"/plugin install meetings@claude-code-skills"
],
"requires": "Python (stdlib) for helper scripts",
"safety": {
"rating": "safe",
"notes": "Python scripts use only standard library (json, argparse, re, csv); no network, no subprocess, no credentials."
},
"cat": "docs",
"official": false
},
{
"name": "linkedin (plugin)",
"url": "https://github.com/alirezarezvani/claude-skills/tree/main/marketing/linkedin",
"stars": 29769,
"license": "MIT",
"last_commit": "2026-11-03",
"maintainer": "Alireza Rezvani (individual, known maintainer; ~2.9k followers)",
"desc_en": "Improves your LinkedIn profile, plans posts, writes and checks content and outreach messages within LinkedIn's rules.",
"desc_pt": "Melhora seu perfil no LinkedIn, planeja posts, escreve e revisa conteúdo e mensagens dentro das regras do LinkedIn.",
"for_whom_en": "Insurance agents, realtors, financial advisors, immigration attorneys.",
"for_whom_pt": "Corretores de seguro e de imóveis, consultores financeiros, advogados de imigração.",
"install_claude_ai": {
"supported": true,
"notes": "Download the skill folder, zip it, then claude.ai Settings > Capabilities > Skills > Upload. Zip individual folders under skills/ (e.g., linkedin-content)."
},
"install_claude_code": [
"/plugin marketplace add alirezarezvani/claude-skills",
"/plugin install linkedin@claude-code-skills"
],
"requires": "Python (stdlib) for analyzers",
"safety": {
"rating": "safe",
"notes": "Stdlib-only Python; explicitly no credentials, no API calls, nothing auto-sent; refuses scraping/automation."
},
"cat": "marketing",
"official": false
},
{
"name": "contract-and-proposal-writer",
"url": "https://github.com/alirezarezvani/claude-skills/tree/main/business-growth/skills/contract-and-proposal-writer",
"stars": 29769,
"license": "MIT",
"last_commit": "2026-10-30",
"maintainer": "Alireza Rezvani (individual, known maintainer; ~2.9k followers)",
"desc_en": "Drafts proposals, scopes of work, simple service contracts and NDAs (US templates) as a starting point for review.",
"desc_pt": "Rascunha propostas, escopos de trabalho, contratos de serviço e NDAs (modelos dos EUA) como ponto de partida para revisão.",
"for_whom_en": "Contractors, cleaning companies, freelancers quoting jobs.",
"for_whom_pt": "Construtores, empresas de limpeza, autônomos fazendo orçamentos.",
"install_claude_ai": {
"supported": true,
"notes": "Download the skill folder, zip it, then claude.ai Settings > Capabilities > Skills > Upload."
},
"install_claude_code": [
"/plugin marketplace add alirezarezvani/claude-skills",
"/plugin install business-growth-skills@claude-code-skills",
"(plugin also includes customer-success, revenue-ops, sales-engineer skills)"
],
"requires": "Optional: pandoc for .docx conversion (or use Anthropic docx skill)",
"safety": {
"rating": "safe-with-notes",
"notes": "Single SKILL.md. Suggests installing pandoc manually (brew/apt) for conversion; nothing auto-installs. Not legal advice: have a Florida attorney review."
},
"cat": "vendas",
"official": false
},
{
"name": "superpowers: brainstorming",
"url": "https://github.com/obra/superpowers/tree/main/skills/brainstorming",
"stars": 317229,
"license": "MIT",
"last_commit": "2026-11-03",
"maintainer": "Jesse Vincent (individual, well-known OSS dev; ~9.5k followers)",
"desc_en": "Turns a rough idea into a clear plan by asking one question at a time before building anything.",
"desc_pt": "Transforma uma ideia solta num plano claro, fazendo uma pergunta por vez antes de construir qualquer coisa.",
"for_whom_en": "Tech-curious students building tools/apps with Claude Code.",
"for_whom_pt": "Alunos curiosos por tecnologia criando ferramentas com o Claude Code.",
"install_claude_ai": {
"supported": false,
"notes": "Part of the Superpowers plugin (software-dev workflow); best in Claude Code."
},
"install_claude_code": [
"/plugin install superpowers@claude-plugins-official",
"(or: /plugin marketplace add obra/superpowers; /plugin install superpowers@superpowers-dev)"
],
"requires": "Claude Code",
"safety": {
"rating": "safe-with-notes",
"notes": "Plugin adds a SessionStart hook that injects the using-superpowers skill text (local file read only). Optional visual-brainstorming local server (127.0.0.1, token-gated) loads a logo image from primeradiant.com, which acts as a usage ping; disable with SUPERPOWERS_DISABLE_TELEMETRY=1. Opens a browser only when opted in."
},
"cat": "tech",
"official": false
},
{
"name": "playwright-skill (browser automation)",
"url": "https://github.com/lackeyjb/playwright-skill/tree/main/skills/playwright-skill",
"stars": 3292,
"license": "MIT",
"last_commit": "2026-08-14",
"maintainer": "Bryan Lackey (individual)",
"desc_en": "Lets Claude open a real browser to test your website or automate repetitive web tasks.",
"desc_pt": "Permite ao Claude abrir um navegador de verdade para testar seu site ou automatizar tarefas repetitivas na web.",
"for_whom_en": "Tech-curious students who have a website or web form to test.",
"for_whom_pt": "Alunos curiosos por tecnologia com site ou formulário para testar.",
"install_claude_ai": {
"supported": false,
"notes": "Needs Node.js and a local browser; Claude Code only."
},
"install_claude_code": [
"/plugin marketplace add lackeyjb/playwright-skill",
"/plugin install playwright-skill@playwright-skill",
"Then run once: npm run setup (inside the skill folder)"
],
"requires": "Claude Code, Node.js, Playwright + Chromium (downloaded by npm setup)",
"safety": {
"rating": "safe-with-notes",
"notes": "run.js executes Claude-written browser scripts locally (by design). Setup is manual (npm install + playwright browser download from npm/Microsoft CDN), not auto-run. Do not point it at sites with your logins or payments."
},
"cat": "tech",
"official": false
}
]
};
