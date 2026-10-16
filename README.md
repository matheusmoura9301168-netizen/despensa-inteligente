# Despensa Inteligente

Organizador de receitas que sugere o que cozinhar com os ingredientes que tens em casa. Feito em Python com CustomTkinter.

Há duas versões da mesma aplicação:

| Pasta | Base de dados | Para quê |
|---|---|---|
| [`versao-sqlite/`](versao-sqlite/) | SQLite | Não precisa de instalar nada além do Python. Código muito comentado. |
| [`versao-postgresql/`](versao-postgresql/) | PostgreSQL em Docker | Estrutura em camadas (models, services, ui) e pgAdmin para ver os dados. |

## Funcionalidades

- **Despensa:** adicionar, editar e remover ingredientes com quantidade e unidade
- **Sugestões:** receitas 100% compatíveis com a despensa ou ordenadas pela percentagem de ingredientes que já tens
- **Detalhe da receita:** tempo, porções, dificuldade, ingredientes e modo de preparação passo a passo
- Receitas portuguesas e internacionais já incluídas (60 na versão SQLite e 20 na versão PostgreSQL)

## Versão SQLite

```bash
pip install customtkinter
cd versao-sqlite
python main.py
```

A base de dados `despensa.db` é criada automaticamente na primeira execução.

## Versão PostgreSQL

Requer Python 3.11+ e Docker Desktop.

```bash
cd versao-postgresql
cp .env.example .env
docker-compose up -d
pip install -r requirements.txt
python app/main.py
```

O pgAdmin fica disponível em http://localhost:5050 (credenciais definidas no `docker-compose.yml`).

Para parar os contentores: `docker-compose down` (ou `docker-compose down -v` para apagar também os dados).

## Estrutura da versão PostgreSQL

```
versao-postgresql/
├── docker-compose.yml   # PostgreSQL + pgAdmin
├── .env.example         # Credenciais da base de dados
├── requirements.txt
└── app/
    ├── main.py          # Ponto de entrada
    ├── database/        # Ligação e migrações
    ├── models/          # Ingrediente e Receita
    ├── services/        # Lógica da despensa e das sugestões
    └── ui/              # Interface gráfica
```
