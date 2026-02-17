# ATK-Pro – Reconstruidor de Ladrilhos Antenati
**Nota:** Este projeto é desenvolvido, mantido e suportado inteiramente por uma única pessoa. Todo feedback, relatório ou contribuição é bem-vindo, mas não há uma equipe ou estrutura corporativa por trás do desenvolvimento.
## Descrição
ATK-Pro é uma ferramenta avançada para a reconstrução, arquivamento e consulta de imagens e documentos genealógicos digitalizados do portal Antenati. O projeto suporta gerenciamento multilíngue e distribuição como um aplicativo independente para Windows.
## Funcionalidades principais
- Reconstrução automática de imagens a partir de tiles IIIF
- Suporte multilíngue (20 idiomas)
- Interface gráfica moderna (Qt)
- Compilar EXE autônomo e instalador multilíngue
## Instalação
1. Baixe o instalador ATK-Pro-Setup-v2.0.exe ou o executável autônomo ATK-Pro.exe da seção de releases.
1. Siga as instruções na tela para completar a instalação.
1. Inicie o ATK-Pro a partir do menu Iniciar ou da pasta de instalação.
## Estrutura do projeto
- `src/` – Código fonte principal (GUI, lógica, módulos)
- `assets/` – Ativos multilíngues (guias, modelos, recursos)
- `locales/` – Arquivos de tradução .ini para cada idioma
- `docs_generali/` – Glossários, documentação geral, roadmap
- `scripts/` – Scripts de manutenção, tradução, validação
- `testes/` – Testes automáticos e de cobertura
- `dist/` – Compilação/instalador de saída
## Documentação
- A documentação histórica e de aprofundamento está agora arquivada em `docs_generali/archivio/`.
- O presente README e o ficheiro `CHANGELOG.md` resumem o estado e as principais etapas do projeto.
## História e desenvolvimento
O projeto nasce como uma evolução de ferramentas para genealogia digital, com atenção à transparência, arquivamento histórico e suporte internacional. Cada marco é rastreado e documentado no repositório.
## Créditos
Desenvolvimento e manutenção: Daniele Pigoli
Contribuições: ver changelog e notas de lançamento
## Registro de alterações
Consulte o arquivo `docs_generali/CHANGELOG.md` para as principais novidades e marcos do projeto.
Para detalhes históricos e notas completas, veja a pasta `docs_generali/archivio/`.

-----
## Estado atual
- Todos os módulos ativos foram testados com cobertura direta e defensiva
- Anotação com bloco `# === Cobertura de teste ===` nos módulos validados
- O módulo main.py, mesmo com cobertura parcial (64%), foi validado logicamente por ser orquestrador
### Próximos passos
- Preparar a v2.1 com evolução incremental e documentação atualizada

✍️ Curado por Daniele Pigoli – com o intuito de unir rigor técnico e memória histórica.
