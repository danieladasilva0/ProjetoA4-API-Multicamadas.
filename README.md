# Projeto A4 — API Multicamadas

Exemplo acadêmico de uma API Python com FastAPI e SQLite, organizada por responsabilidade, publicada por Nginx e monitorada com Prometheus e Grafana.

## Arquitetura

```text
Cliente
  └── Nginx (:8080) ──proxy──> FastAPI/Uvicorn (:8000, rede interna)
                                  ├── /registros → rota → serviço → repositório → SQLite
                                  ├── /health → rota → serviço → repositório → SQLite
                                  └── /metrics → métricas Prometheus
Prometheus (:9090) ──coleta──> API:8000/metrics
Grafana (:3000) ──consulta──> Prometheus
```

As rotas ficam em `src/app/api`, os contratos Pydantic em `src/app/models`, as regras de negócio em `services`, o acesso ao SQLite em `repositories`, configurações comuns em `core` e métricas/logs em `middleware`. A tabela `registros` é preparada quando a API inicia; `/health` testa a conexão com o banco.

O CRUD de `/registros` foi adaptado do [repositório de origem](https://github.com/fvaladares/ApitUniBHSD202602), mantendo os campos `titulo`, `descricao` e `ativo` e organizando a implementação em camadas:

| Método | Rota | Ação |
| --- | --- | --- |
| `POST` | `/registros` | Cria registro (201; título em branco retorna 400) |
| `GET` | `/registros` | Lista registros |
| `GET` | `/registros/{id}` | Busca por ID (404 quando não existe) |
| `PUT` | `/registros/{id}` | Atualiza por ID (404 quando não existe) |
| `DELETE` | `/registros/{id}` | Exclui por ID (404 quando não existe) |

## Requisitos

- Docker com o plugin Docker Compose
- Git (opcional, para trabalhar com branches)

## Instalar e configurar

1. Clone o projeto e entre na pasta:

   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd ProjetoA4-API-Multicamadas
   ```

2. Crie o arquivo local de configuração do Grafana:

   ```bash
   cp .env.example .env
   ```

   Edite `.env` e troque `GRAFANA_ADMIN_PASSWORD` por uma senha sua. Não envie o `.env` ao Git.

3. Construa e inicie os serviços:

   ```bash
   docker compose up --build -d
   docker compose ps
   ```

## Acessar e validar

- API pelo proxy Nginx: <http://localhost:8080/health>
- CRUD pelo proxy Nginx: <http://localhost:8080/registros>
- Documentação interativa: <http://localhost:8080/docs>
- Métricas da API pelo proxy: <http://localhost:8080/metrics>
- Prometheus: <http://localhost:9090/targets>
- Grafana: <http://localhost:3000> (usuário e senha definidos no `.env`)

O alvo `fastapi` deve aparecer como **UP** em `/targets`. No Grafana, abra a pasta **Projeto A4** e o dashboard **API — Observabilidade**. Ele contém três painéis:

1. Vazão de requisições por segundo.
2. Taxa de respostas HTTP 4xx e 5xx.
3. Latência média das respostas.

Para criar e listar registros, além de gerar tráfego para o dashboard:

```bash
curl -X POST http://localhost:8080/registros \
  -H 'Content-Type: application/json' \
  -d '{"titulo":"Primeiro registro","descricao":"Exemplo","ativo":true}'
curl http://localhost:8080/registros
curl http://localhost:8080/rota-inexistente
```

As métricas são agregadas em janelas de tempo; pode levar um ou dois minutos para os gráficos mostrarem os primeiros pontos.

## Executar no Replit para desenvolvimento

O workflow do Replit inicia o Uvicorn atrás do Nginx na porta de preview 5000. O acesso pelo preview segue o mesmo proxy reverso. Para executar testes localmente:

```bash
uv sync --extra dev
uv run pytest
```

O Compose continua sendo a forma de subir Prometheus e Grafana. No Replit, também é possível rodar os testes com `uv run pytest`.

## Logs, métricas e persistência

O middleware registra método, rota, status e duração em logs JSON no stdout, usando Loguru. Ele também coleta `http_requests_total` e `http_request_duration_seconds`; o Prometheus lê essas métricas a cada 15 segundos. A rota `/metrics` é usada pelo Prometheus e também passa pelo Nginx quando acessada externamente.

O Nginx é o único serviço que publica a API no host. Uvicorn fica acessível apenas na rede interna do Compose; Prometheus consulta a API diretamente nessa rede. Grafana consulta Prometheus pela rede interna. Volumes do Compose preservam o banco SQLite e os dados das ferramentas entre reinicializações.

## Parar os serviços

```bash
docker compose down
```

Para apagar também os dados persistidos do SQLite, Prometheus e Grafana, use `docker compose down -v`. Esse comando remove os volumes e seus dados.
