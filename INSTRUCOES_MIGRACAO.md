# INSTRUÇÕES PARA MIGRAÇÃO - SQLite para Access

## Pré-requisitos

### 1. Microsoft Access Database Engine
Para conectar com bancos Access, é necessário instalar o **Microsoft Access Database Engine**:

**Opção A: Se você tem Microsoft Office/Access instalado**
- Não é necessário instalar nada adicional

**Opção B: Se você NÃO tem Microsoft Office/Access instalado**
- Baixe e instale o **Microsoft Access Database Engine 2016 Redistributable**
- Link: https://www.microsoft.com/en-us/download/details.aspx?id=54920
- Escolha a versão de acordo com seu sistema (32-bit ou 64-bit)

### 2. Python Packages
O script de migração instalará automaticamente:
- `pyodbc` - Driver principal para Access
- `pypyodbc` - Driver alternativo caso o primeiro falhe

## Como Executar a Migração

### Passo 1: Executar o Script de Migração
```cmd
python migrate_to_access.py
```

### Passo 2: Acompanhar o Processo
O script irá:

1. **Criar backup** do sistema atual (SQLite + arquivos)
2. **Instalar dependências** Python necessárias
3. **Criar banco Access** vazio com todas as tabelas
4. **Migrar dados** do SQLite para Access
5. **Atualizar sistema** para usar Access
6. **Verificar migração** para garantir que funcionou

### Passo 3: Testar o Sistema
Após a migração, teste:
```cmd
python main.py
```

## Estrutura Após a Migração

```
sisproj_pf/
├── sisproj_pf.accdb          # ← NOVO: Banco Access
├── sisproj_pf.db             # ← Banco SQLite original (mantido como backup)
├── backup_YYYYMMDD_HHMMSS/   # ← Backup completo do sistema anterior
│   ├── sisproj_pf.db
│   └── db_manager_sqlite.py
├── models/
│   ├── db_manager.py         # ← MODIFICADO: Agora usa Access
│   └── db_manager_access.py  # ← Código específico para Access
└── migrate_to_access.py      # ← Script de migração
```

## Vantagens do Access vs SQLite

### Access (.accdb)
✅ Interface visual para consultas e relatórios
✅ Melhor integração com Microsoft Office
✅ Controle de acesso mais robusto
✅ Suporte nativo a tipos de dados complexos
✅ Ferramentas de análise integradas

### SQLite (.db)
✅ Mais leve e portável
✅ Não requer drivers externos
✅ Melhor performance para operações simples
✅ Multiplataforma sem dependências

## Solução de Problemas

### Erro: "Driver não encontrado"
- Instale o Microsoft Access Database Engine
- Certifique-se de usar a versão correta (32/64-bit)

### Erro: "Permissão negada"
- Execute como administrador
- Verifique se o arquivo .accdb não está aberto em outro programa

### Erro: "Tabela não encontrada"
- Execute novamente o script de migração
- Verifique se o arquivo sisproj_pf.accdb foi criado

### Performance Lenta
- Access pode ser mais lento que SQLite para muitas operações
- Considere criar índices nas colunas mais consultadas
- Compacte o banco periodicamente (Tools > Database Tools > Compact)

## Backup e Manutenção

### Backup Regular
```cmd
# Crie backups regulares do arquivo .accdb
copy sisproj_pf.accdb backup_sisproj_pf_%date%.accdb
```

### Compactação do Banco
- Periodicamente, abra o arquivo .accdb no Access
- Vá em Database Tools > Compact and Repair Database

### Monitoramento
- Acompanhe o tamanho do arquivo .accdb
- Access tem limite de 2GB por arquivo
- Se necessário, considere dividir em múltiplos bancos

## Contato e Suporte

Em caso de problemas:
1. Verifique se seguiu todos os pré-requisitos
2. Execute o script com privilégios de administrador
3. Consulte os logs de erro detalhados
4. Mantenha backup do sistema SQLite original 