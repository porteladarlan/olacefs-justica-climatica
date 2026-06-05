# Preparação do ambiente de teste externo

## Objetivo

Este documento orienta a preparação do ambiente antes de convidar pessoas externas para testar a plataforma.

## Passo 1 — Atualizar código

Garantir que a branch `main` esteja atualizada e validada:

```powershell
git checkout main
git pull origin main
python manage.py test
```

## Passo 2 — Carregar dados demonstrativos

Para demonstração local ou ambiente de teste:

```powershell
python manage.py carregar_dados_ficticios --limpar-demo
```

## Passo 3 — Rodar auditorias

```powershell
python manage.py auditar_traducoes_trilingues
python manage.py auditar_autenticacao_perfis
python manage.py validar_fluxo_ponta_a_ponta
```

## Passo 4 — Validar páginas principais

Testar manualmente:

- `/`
- `/catalogo/`
- `/banco-tecnico/`
- `/normas-internacionais/`
- `/sobre/`
- `/cadastro/`
- `/entrar/`
- `/adicionar-boa-pratica/`
- `/meus-envios/`
- `/painel-revisao/`
- `/painel-revisao-edicoes/`

Também testar:

- `/en/`
- `/es/`

## Passo 5 — Perfis de teste

Preparar pelo menos:

1. Usuário comum/autor:
   - testa cadastro/login;
   - envia boa prática;
   - salva rascunho;
   - envia para revisão.

2. Usuário staff/revisor:
   - acessa painel de revisão;
   - revisa submissões;
   - solicita ajustes;
   - aprova/publica.

## Passo 6 — Limitações atuais a comunicar

Antes do teste, informar:

- o ambiente é de validação;
- os dados são demonstrativos;
- recursos técnicos e normas ainda estão em curadoria;
- a publicação real depende de revisão institucional;
- anexos e arquivos devem ser testados com cautela conforme configuração do ambiente;
- produção real futura ainda exige definição de hospedagem, banco persistente, backups, domínio e governança.

## Passo 7 — Coleta de retorno

Enviar às pessoas testadoras:

- roteiro de teste;
- checklist;
- perguntas de feedback.

Recomenda-se consolidar os retornos em uma planilha ou formulário.
