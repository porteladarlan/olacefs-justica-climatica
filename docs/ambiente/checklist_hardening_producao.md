# Checklist de hardening para produção futura

## Bloqueantes antes de produção

- [ ] Remover edição por e-mail simples em query string.
- [ ] Exigir login ou token assinado para editar submissões.
- [ ] Restringir `ALLOWED_HOSTS` ao domínio oficial.
- [ ] Definir `SECRET_KEY` somente por variável segura.
- [ ] Usar PostgreSQL persistente.
- [ ] Usar storage persistente para anexos.
- [ ] Configurar backup e restore testado.
- [ ] Definir política de retenção de anexos.
- [ ] Definir governança editorial formal.
- [ ] Revisar privacidade/termos de uso.

## Recomendados

- [ ] Validar MIME de arquivos enviados.
- [ ] Aplicar varredura antimalware em anexos.
- [ ] Configurar logs estruturados.
- [ ] Configurar monitoramento de erros.
- [ ] Configurar alertas de disponibilidade.
- [ ] Definir grupos/permissões além de `is_staff`.
- [ ] Habilitar `SECURE_SSL_REDIRECT=True` em HTTPS definitivo.
- [ ] Habilitar HSTS após confirmar domínio e subdomínios.
- [ ] Revisar limites de upload e payload.
- [ ] Revisar dependências periodicamente.

## Comandos de validação

```powershell
python manage.py test
python manage.py auditar_traducoes_trilingues
python manage.py auditar_autenticacao_perfis
python manage.py validar_fluxo_ponta_a_ponta
python manage.py checar_prontidao_ambiente
python manage.py auditar_render_publico --url https://olacefs-justica-climatica.onrender.com/
```
