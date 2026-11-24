# Rastreabilidade entre o TCC e a implementação

Esta matriz relaciona os parâmetros P01-P16, os itens da planilha de auditoria,
as regras implementadas e a evidência necessária. O estado de cobertura se
refere à versão atual do repositório e não representa conformidade do terminal.

| Parâmetro | Tema | IDs da planilha | Regra ou instrumento | Cobertura atual | Evidência necessária |
|---|---|---|---|---|---|
| P01 | Depuração do APK | APP-01 | APK-001 | Automática | Atributo `android:debuggable` do APK final e hash do artefato |
| P02 | Backup | APP-02, DAT-05 | APK-002 | Parcial | `allowBackup`, regras de extração e teste conforme versão/fabricante |
| P03 | Permissões | APP-04 | APK-003 | Automática no perfil | Ausência de permissões perigosas; `INTERNET` normal permanece permitida |
| P04 | Componentes exportados | APP-05 | KIOSK-002 | Automática no perfil | Nenhum componente interno exportado; launcher esperado é excluído da regra |
| P05 | Credenciais | APP-07, OPS-03 | APK-004 e revisão complementar | Automática delimitada | Literais compatíveis com os padrões definidos; revisar ofuscação e valores dinâmicos |
| P06 | Dados e logs | APP-10, DAT-01, DAT-04 | Revisão/teste manual | Manual | Arquivos, preferências, bancos, cache, Logcat, retenção e destinos |
| P07 | Sessões | Sem item específico na planilha | Teste dinâmico | Não implementada | Estado antes/depois da troca, abandono e encerramento do atendimento |
| P08 | Plataforma | KSK-06, KSK-07, OPS-02 | ADB Probe e verificação do fornecedor | Parcial | Versão, SDK, atualização, imagem, pacotes e situação de suporte |
| P09 | ADB | KSK-08, PHY-02 | ADB Probe e inspeção da configuração | Parcial | Estado do ADB e propriedades antes/depois da manutenção |
| P10 | Confinamento kiosk | KSK-01, KSK-02, KSK-03, KSK-04 | KIOSK-001 catalogada; teste manual | Não automatizada | Lock task, rotas de saída, interrupções, reinício e acesso a configurações |
| P11 | Políticas | KSK-05, OPS-04 | ADB Probe e configuração administrativa | Parcial | Device Owner/MDM, allowlist, responsável e políticas ativas |
| P12 | Interfaces físicas | GOV-03, PHY-01, PHY-03, PHY-04 | Inspeção física | Manual | Gabinete, USB, boot/recovery, periféricos e controles de acesso |
| P13 | Texto claro | APP-03, NET-01, NET-03 | Configuração do manifesto e indicadores DEX | Parcial | Política de rede, URLs e tráfego efetivamente observado |
| P14 | Autenticidade da conexão | NET-02 | Teste TLS dinâmico | Não implementada | Certificados válidos, inválidos, expirados e hostname incompatível |
| P15 | Atualizações | APP-11, OPS-01, OPS-02 | Revisão de processo e teste controlado | Manual | Origem, assinatura, integridade, falha, recuperação e compatibilidade |
| P16 | Intervenção | PHY-05, AUD-03, AUD-04, AUD-05 | Revisão de processo e revalidação | Manual | Autorização, registros, mudanças e restauração das restrições kiosk |

## Interpretação dos estados

- **Automática:** a regra produz evidência direta para o critério delimitado.
- **Parcial:** a ferramenta coleta um indicador, mas a conclusão exige contexto
  ou procedimento complementar.
- **Manual:** a avaliação depende de inspeção, revisão ou teste fora do auditor.
- **Não implementada:** ainda não existe procedimento executável no repositório.

Uma regra automática não transforma, sozinha, o parâmetro em “conforme” ou “não
conforme”. Falha de coleta e ausência de achado devem ser registradas como “não
avaliado” quando não houver evidência suficiente.

No perfil de referência, P03 e P04 possuem critérios estáticos conclusivos. P05
é conclusivo apenas para os padrões de literais estáticos documentados; a
ausência de correspondência não exclui segredos ofuscados, construídos em
execução ou recebidos remotamente.

## Estados de avaliação dos relatórios

- `conforme`: evidência suficiente produzida por uma verificação conclusiva;
- `nao_conforme`: descumprimento demonstrado por uma verificação conclusiva;
- `nao_avaliado`: evidência ausente, incompleta ou apenas indicativa;
- `nao_aplicavel`: exclusão justificada e registrada por uma pessoa responsável.

O programa nunca atribui `nao_aplicavel` automaticamente. A severidade das
regras é usada como prioridade inicial de triagem, não como métrica universal
validada de risco.
