# Percurso teórico sem VM ou sem permissões

Este percurso é uma atividade completa de análise. Não execute supervisor, fixtures
ou scripts de inventário no host. Você pode ler fontes, desenhar estados,
compilar com `make -C materials` e verificar sintaxe. Marque a execução prática como
**não verificada**. Se a VM existir mas um mecanismo não estiver autorizado, preserve
as evidências dos mecanismos disponíveis e aplique este percurso aos restantes.

1. **Defina ameaça e ativos.** Escreva quais arquivos, credenciais, file descriptors, CPU,
   memória e processos pretende proteger. Separe o modelo benigno do contrato de
   um programa adversarial que troca grupo, cria muitos filhos ou tenta acessar a rede.
2. **Desenhe a máquina de estados.** Inclua validação, preparação, filho bloqueado,
   exec, espera, prazo, término do principal, limpeza e reaping. Para cada transição,
   indique o recurso adquirido, quem tem ownership dele e a recuperação se a próxima operação falhar.
3. **Simule quatro traces à mão.** Use saída 7 sem descendente; filho ignorando SIGTERM
   até SIGKILL; principal saindo antes do filho; falha de setrlimit após fork.
   Indique processos vivos e zombies após cada evento. Justifique quem pode usar waitpid.
4. **Compare limites.** Calcule o teto virtual de dois processos com 64 MiB cada e
   explique por que isso não equivale a 64 MiB agregados nem a RSS observado. Compare
   um processo que dorme dois segundos com um que consome um segundo de CPU.
5. **Complete a matriz de mecanismos.** Use a tabela do [roteiro](README.md) para
   rlimits, namespaces, cgroup v2 e seccomp. Em vez de saídas inventadas, escreva
   “previsão documental” e cite o trecho pertinente das [referências](../references.md).
6. **Leia código real.** Localize no Bubblewrap os flags de clone, `setup_newroot`,
   `close_ops_fd` e a instalação de seccomp. Desenhe a ordem relativa; descreva uma
   condição que o núcleo didático não trata. Não copie a implementação como solução.
7. **Escreva o plano de execução futura.** Liste VM, usuário, snapshot, ausência de
   compartilhamentos, permissões, comandos do pacote, resultados esperados e descarte.
   Identifique quais casos exigem teste adicional ou revisão manual.

O percurso está concluído quando o relatório contém os sete itens, a origem das
afirmações, os estados após erros e pelo menos um limite de cada mecanismo. O revisor
deve conseguir distinguir hipótese, consequência do contrato e regra documentada.
Não é necessário possuir VM para concluir esta análise; a conclusão do supervisor
prático continua dependendo de execução na VM.

Inclua literalmente no relato: “A solução didática não é adequada para execução de
código adversarial em produção sem arquitetura, revisão e isolamento adicionais.”
