-- Criação do Banco de Dados
CREATE DATABASE nome_do_banco;

-- Conecte-se ao banco de dados antes de prosseguir
\c nome_do_banco;

-- Tabela de Usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    nome_responsavel VARCHAR(100) NOT NULL,
    senha VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Estabelecimentos
CREATE TABLE IF NOT EXISTS estabelecimentos (
    id SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL,
    nome VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE,
    UNIQUE (id_usuario)
);

-- Tabela de Mídias
CREATE TABLE IF NOT EXISTS midias (
    id SERIAL PRIMARY KEY,
    id_usuario INTEGER NOT NULL,
    id_estabelecimento INTEGER NOT NULL,
    url VARCHAR(255) NOT NULL,
    tipo_midia VARCHAR(20) CHECK (tipo_midia IN ('imagem', 'video')),
    data_upload TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (id_estabelecimento) REFERENCES estabelecimentos(id) ON DELETE CASCADE
);

-- Tabela de Logs de Exibição de Mídia (para relatórios)
CREATE TABLE IF NOT EXISTS logs_exibicao (
    id SERIAL PRIMARY KEY,
    id_midia INTEGER NOT NULL,
    id_usuario INTEGER NOT NULL,
    inicio_exibicao TIMESTAMP NOT NULL,
    fim_exibicao TIMESTAMP NOT NULL,
    FOREIGN KEY (id_midia) REFERENCES midias(id) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Inserção de um usuário admin padrão
INSERT INTO usuarios (username, nome_responsavel, senha, role)
VALUES ('santosmidia', 'Admin', '123456', 'admin')
ON CONFLICT (username) DO NOTHING;

-- Inserção de um estabelecimento padrão para o admin
INSERT INTO estabelecimentos (id_usuario, nome, tipo)
VALUES (
    (SELECT id FROM usuarios WHERE username = 'santosmidia'),
    'Admin Central',
    'admin'
) ON CONFLICT (id_usuario) DO NOTHING;