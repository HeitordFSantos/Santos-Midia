# Flask Render PostgreSQL

Este projeto é uma aplicação Flask hospedada no Render, com PostgreSQL como banco de dados e Cloudinary para armazenamento de arquivos. A aplicação permite upload de imagens e vídeos, com diferentes tipos de acesso (admin e usuário).

## Funcionalidades

- **Login:** Acesso com credenciais de admin ou usuário.
- **Admin:** Capacidade de fazer upload de arquivos (imagens/vídeos) para o Cloudinary.
- **Usuário:** Visualização dos arquivos enviados.
- **Banco de Dados PostgreSQL:** Armazena informações dos usuários e links para os arquivos no Cloudinary.

## Como usar

1. Clone este repositório.
2. Instale as dependências: `pip install -r requirements.txt`
3. Configure as variáveis de ambiente no arquivo `.env`.
4. Execute o servidor Flask: `flask run`

## Configuração no Render

- Crie um serviço no Render para hospedar a aplicação.
- Adicione as variáveis de ambiente necessárias (CLOUD_NAME, API_KEY, API_SECRET, DATABASE_URL).
