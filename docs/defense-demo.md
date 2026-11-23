# Roteiro de demonstração para a defesa

Este roteiro apresenta a prova de conceito em aproximadamente cinco minutos.
Ele demonstra o recorte automatizado do framework, sem afirmar validação
integral dos parâmetros P01-P16.

## Preparação antes da apresentação

1. Configure o Android SDK conforme `docs/android-build.md`.
2. Ative o ambiente Python com o projeto e as dependências instaladas.
3. Execute a validação completa pelo menos uma vez:

```bash
./scripts/validate_project.sh
```

4. Confirme que os três JSONs e o resumo em `reports/` estão presentes.
5. Mantenha os relatórios versionados como alternativa caso a rede, o SDK ou o
   projetor causem problemas durante a demonstração.

## Demonstração sugerida

### 1. Apresente a contribuição

Explique em uma frase:

> O trabalho organiza 16 parâmetros de segurança em seis camadas e utiliza o
> auditor como prova de conceito para coletar parte das evidências verificáveis
> por software.

Mostre `docs/tcc-traceability.md` e destaque que a matriz separa verificações
automáticas, parciais, manuais e ainda não implementadas.

### 2. Mostre os cenários controlados

Apresente os manifestos dos dois aplicativos:

- o vulnerável contém depuração, backup, permissões perigosas e componentes
  internos exportados propositalmente;
- o endurecido desativa depuração e backup, reduz permissões, restringe
  componentes e bloqueia tráfego em texto claro.

Deixe claro que os aplicativos são cenários sintéticos e não representam
terminais comerciais.

### 3. Execute os testes

```bash
pytest -q
```

Resultado esperado: 14 testes aprovados.

### 4. Gere novamente as evidências

Se os APKs já estiverem compilados:

```bash
python -m apk_analyzer.cli \
  --vulnerable vulnerable-kiosk-app/app/build/outputs/apk/debug/app-debug.apk \
  --hardened hardened-kiosk-app/app/build/outputs/apk/debug/app-debug.apk
```

Mostre `reports/apk-comparison-summary.md`.

### 5. Interprete o resultado

No cenário vulnerável, as dez ocorrências das regras implementadas são:

- uma aplicação depurável;
- backup habilitado;
- seis permissões perigosas;
- dois componentes internos exportados.

No cenário endurecido, nenhuma dessas ocorrências foi detectada. A avaliação,
contudo, registra somente P01 como `conforme`; os outros três controles ficam
`nao_avaliado` porque exigem contexto adicional.

### 6. Encerre com os limites

> A prova de conceito demonstra coleta reproduzível de evidências estáticas. Ela
> não certifica o aplicativo nem substitui testes de dispositivo, confinamento
> kiosk, TLS, comportamento em execução, inspeção física ou processos de
> manutenção.

## Perguntas previsíveis da banca

### Por que zero achados não significa segurança?

Porque o resultado cobre somente as regras executadas. Controles dinâmicos,
físicos, administrativos e de dispositivo permanecem fora desse resultado.

### Por que permissões e componentes exportados ficam “não avaliados”?

Porque podem ser funcionalmente necessários e estar protegidos corretamente.
O detector identifica o indicador; a conclusão depende da finalidade, dos
controles de acesso e de testes de invocação.

### Qual é a contribuição principal?

O catálogo contextualizado P01-P16, sua organização em seis camadas e o processo
de coleta, interpretação, tratamento e reavaliação. O auditor é um instrumento
auxiliar da demonstração.

### A ferramenta substitui uma análise de segurança completa?

Não. Ela automatiza parte da coleta estática e oferece estruturas para futuras
extensões. O framework exige instrumentos complementares.

### Como o experimento pode ser reproduzido?

O repositório fixa as versões de Gradle, plugin Android, SDK e Build Tools,
compila os dois APKs, calcula seus hashes e regenera os relatórios por um comando
documentado.

### Como são tratados falsos positivos?

O relatório diferencia achado, indicador e estado de avaliação. Por exemplo, a
`MainActivity` do launcher não é tratada como componente interno exposto. Regras
indicativas não atribuem conformidade ou não conformidade automaticamente.

### A severidade representa risco universal?

Não. É uma prioridade inicial de triagem. A avaliação de risco depende da
exposição, do impacto, da função do terminal e das condições de exploração.

## Plano de contingência

Se a compilação não puder ser executada durante a defesa:

1. mostre os hashes e horários nos relatórios versionados;
2. execute apenas `pytest -q`, que não depende do SDK Android;
3. apresente o resumo comparativo já gerado;
4. explique que o build completo foi validado previamente no ambiente
   documentado.
