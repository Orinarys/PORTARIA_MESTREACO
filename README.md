# SISTEMA DE PORTARIA - MANUAL DE INSTALAÇÃO E USO

## 📋 Descrição
Sistema completo de controle de portaria para registro de entrada e saída de clientes e visitantes, com validação de CPF e banco de dados local.

## 🚀 Funcionalidades

### ✅ Recursos Principais
- ✔️ Registro de nome do cliente
- ✔️ Registro da empresa de origem
- ✔️ Validação de CPF via API externa
- ✔️ Registro de telefone com formatação automática
- ✔️ Classificação entre Cliente Ativo e Visitante
- ✔️ Seleção de vendedor responsável (lista predefinida)
- ✔️ Registro de NF de saída
- ✔️ Controle de horário de entrada e saída
- ✔️ Consulta e busca de registros históricos
- ✔️ Banco de dados SQLite local (não requer servidor)

### 👥 Lista de Vendedores
O sistema possui os seguintes vendedores cadastrados:
- THIAGO MOTA
- PRISCILA ARAUJO
- TAIS ARAUJO
- MARIA JULIA SOARES
- CLAUDINEI CRUZ
- ALEXANDRE
- JOSE ADRIANO
- KEVIN SILVA
- EROS RODRIGUES
- DANILO ANDRADE
- ANSELMO CUNHA
- FERNANDA TAVARES

## 📥 Instalação

### Pré-requisitos
- Python 3.7 ou superior instalado
- Conexão com internet (apenas para validação de CPF)

### Passo a Passo

#### Windows:

1. **Baixar Python**
   - Acesse: https://www.python.org/downloads/
   - Baixe e instale a versão mais recente
   - ⚠️ IMPORTANTE: Marque a opção "Add Python to PATH" durante instalação

2. **Instalar dependências**
   ```cmd
   python -m pip install -r requirements.txt
   ```

3. **Executar o sistema**
   ```cmd
   python sistema_portaria.py
   ```

#### Linux/Mac:

1. **Instalar dependências**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Executar o sistema**
   ```bash
   python3 sistema_portaria.py
   ```

## 📖 Como Usar

### Registrando uma Entrada

1. **Preencher dados do cliente:**
   - Nome completo do cliente
   - Nome da empresa de origem
   - CPF (será formatado automaticamente)
   - Telefone (será formatado automaticamente)

2. **Validar CPF:**
   - Clique no botão "Validar CPF"
   - Sistema verifica se o CPF é válido
   - ✅ Verde = CPF válido
   - ❌ Vermelho = CPF inválido
   - 🟧 Laranja = CPF válido (verificação offline)

3. **Selecionar tipo de pessoa:**
   - Cliente Ativo
   - Visitante

4. **Informações de atendimento:**
   - Selecione o vendedor responsável
   - Digite o número da NF de saída

5. **Horários:**
   - Horário de entrada (preenchido automaticamente com hora atual)
   - Horário de saída (opcional, pode ser preenchido depois)
   - Use o botão "Hora Atual" para atualizar rapidamente

6. **Finalizar:**
   - Clique em "REGISTRAR ENTRADA"
   - Sistema confirmará o registro

### Consultando Registros

1. Clique no botão "CONSULTAR REGISTROS"
2. Use o campo de busca para filtrar por:
   - Nome do cliente
   - Nome da empresa
   - CPF
   - NF de saída
3. Clique em "Buscar" para filtrar
4. Clique em "Mostrar Todos" para ver todos os registros

### Limpando Campos

- Clique em "LIMPAR CAMPOS" para resetar o formulário
- Útil para registrar uma nova entrada rapidamente

## 💾 Banco de Dados

### Localização
- Arquivo: `portaria.db`
- Criado automaticamente na mesma pasta do sistema

### Estrutura da Tabela
```sql
registros (
    id                 - Código único do registro
    nome_cliente       - Nome completo do cliente
    empresa            - Nome da empresa
    cpf                - CPF (apenas números)
    telefone           - Telefone de contato
    tipo_pessoa        - Cliente Ativo ou Visitante
    vendedor           - Nome do vendedor responsável
    nf_saida           - Número da Nota Fiscal
    horario_entrada    - Hora de entrada (HH:MM)
    horario_saida      - Hora de saída (HH:MM)
    data_registro      - Data do registro
    cpf_valido         - Indicador se CPF foi validado
)
```

### Backup
Para fazer backup dos dados:
1. Copie o arquivo `portaria.db`
2. Guarde em local seguro
3. Para restaurar, basta copiar o arquivo de volta

## 🔧 Recursos Técnicos

### Validação de CPF
- Validação matemática local (algoritmo de dígito verificador)
- Validação via API externa (quando disponível)
- Funciona offline se a API estiver indisponível

### Formatação Automática
- **CPF**: 000.000.000-00
- **Telefone**: (00) 00000-0000

### Interface
- Interface gráfica moderna e intuitiva
- Organizada por seções
- Campos obrigatórios marcados com *
- Mensagens de erro e sucesso claras

## ⚠️ Solução de Problemas

### "Python não é reconhecido como comando"
- Reinstale o Python marcando "Add to PATH"
- Ou use o caminho completo: `C:\Python3X\python.exe`

### "Erro ao validar CPF"
- Verifique sua conexão com internet
- Sistema funciona offline com validação local

### "Erro ao salvar registro"
- Verifique se todos os campos obrigatórios estão preenchidos
- Certifique-se que tem permissão de escrita na pasta

### Banco de dados não abre
- Verifique se o arquivo `portaria.db` não está aberto em outro programa
- Verifique permissões da pasta

## 📞 Campos Obrigatórios

Os seguintes campos são **obrigatórios** para registrar uma entrada:
- ✅ Nome do Cliente
- ✅ Empresa
- ✅ CPF (válido)
- ✅ Telefone
- ✅ Vendedor
- ✅ NF de Saída
- ✅ Horário de Entrada

O campo **Horário de Saída** é opcional.

## 🎨 Características Visuais

### Cores do Sistema
- **Azul escuro**: Cabeçalhos e títulos
- **Azul claro**: Botões de ação
- **Verde**: Botão de salvar e status positivo
- **Vermelho**: Botão de limpar e avisos
- **Roxo**: Botão de consulta

### Organização
- Interface dividida em seções lógicas
- Scroll automático para telas menores
- Layout responsivo e profissional

## 📊 Relatórios e Consultas

O sistema permite:
- Visualizar todos os registros
- Filtrar por qualquer campo
- Ver histórico completo de entradas/saídas
- Identificar rapidamente status de CPF

## 🔐 Segurança

- Dados armazenados localmente
- Sem acesso remoto
- Validação rigorosa de CPF
- Registro de data e hora automático

## 📝 Dicas de Uso

1. **Use a validação de CPF** antes de salvar para garantir dados corretos
2. **O horário de entrada** é preenchido automaticamente, mas pode ser alterado
3. **Preencha o horário de saída** quando o cliente sair
4. **Use a consulta** para verificar se um cliente já está registrado
5. **Faça backup** regularmente do arquivo `portaria.db`

## 🆘 Suporte

Em caso de dúvidas ou problemas:
1. Verifique se seguiu todos os passos de instalação
2. Confira se tem todos os campos obrigatórios preenchidos
3. Verifique se o Python está instalado corretamente
4. Certifique-se que tem as dependências instaladas

---

**Desenvolvido para controle eficiente de portaria**
Versão 1.0 - 2025
