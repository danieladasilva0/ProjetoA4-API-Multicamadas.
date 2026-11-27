# Executar este projeto no Replit

- O workflow **Start application** inicia a API com Uvicorn e publica o preview através do Nginx na porta 5000.
- A rota principal de verificação é `/health`; a documentação interativa está em `/docs` e as métricas em `/metrics`.
- Para instalar dependências de desenvolvimento e executar os testes: `uv sync --extra dev` e `uv run pytest`.
- Para subir a configuração completa com Nginx, Prometheus e Grafana: configure `GRAFANA_ADMIN_PASSWORD` em um `.env` local e execute `docker compose up --build -d`.
- Os serviços do Compose usam volumes nomeados para persistir SQLite, Prometheus e Grafana.
