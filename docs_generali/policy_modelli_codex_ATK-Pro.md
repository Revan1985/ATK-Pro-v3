# Policy uso modelli Codex per ATK-Pro

Data snapshot: 2026-06-28

Questa policy serve a contenere il consumo di quota durante lo sviluppo di
ATK-Pro senza abbassare la qualita' delle decisioni tecniche. Non impone un
modello obbligatorio: prima dei passaggi non banali l'assistente segnala il
modello consigliato, poi l'utente decide se conformare il modello in uso.

I nomi, i costi e i limiti dei modelli possono cambiare. Questa policy e'
quindi operativa, non definitiva: va riverificata periodicamente rispetto alla
documentazione OpenAI/Codex aggiornata e all'esperienza reale sul progetto.

## Regola pratica

Usare il modello meno costoso che sia ancora adeguato alla fase corrente.

In apertura di un passaggio non banale, l'assistente deve indicare:

```text
Modello consigliato: GPT-5.4 mini | GPT-5.4 | GPT-5.5
Motivo: breve spiegazione del tipo di lavoro e del rischio.
```

Se il lavoro e' minimo, per esempio una risposta discorsiva o un comando
semplice, la segnalazione puo' essere omessa.

## Criteri di scelta

| Tipo di lavoro | Modello consigliato | Motivo |
| --- | --- | --- |
| Ricognizione file, scansioni, conteggi, ricerca occorrenze, sintesi di documenti | GPT-5.4 mini | Prevalentemente lettura e classificazione, rischio basso. |
| Modifiche meccaniche, documentazione, refusi, aggiornamenti tabelle, test ripetitivi | GPT-5.4 mini | Operazioni delimitate e verificabili. |
| Bug con causa nota, fix circoscritto, nuovo test di regressione, packaging ordinario | GPT-5.4 | Serve buona affidabilita' di coding, ma il perimetro e' chiaro. |
| Nuovo portale simile a quelli esistenti, modifica su due o tre moduli coordinati | GPT-5.4 | Richiede contesto del progetto e test mirati, ma non ridisegno generale. |
| GUI + worker + rete, concorrenza, crash non riproducibile, regressione multi-portale | GPT-5.5 | Alto rischio di effetti trasversali e diagnosi ambigua. |
| Refactoring architetturale, policy provider, pipeline manifest/canvas/download/PDF | GPT-5.5 | La decisione puo' propagarsi in molti moduli e test. |
| Revisione finale di diff ampio o release candidate delicata | GPT-5.5 | Meglio massimizzare la qualita' della revisione prima del merge/tag. |

## Fast mode

Fast mode resta disattivata di default. Si valuta solo quando il vincolo
principale e' la latenza e non la quota, per esempio in una sessione breve con
molte attese ma rischio tecnico basso.

## Applicazione nel lavoro quotidiano

- Per i passetti piccoli, indicare il modello consigliato e procedere.
- Per interventi con rischio medio, indicare modello consigliato, perimetro e
  test attesi prima di modificare.
- Per interventi con rischio alto, segnalare esplicitamente che sarebbe
  opportuno usare GPT-5.5 prima di entrare nel refactoring o nel debug profondo.
- Non bloccare automaticamente il lavoro se il modello effettivo e' diverso:
  la scelta finale resta dell'utente.
- Se durante il lavoro emerge che il problema e' piu' trasversale del previsto,
  fermarsi, segnalarlo e rivalutare il modello consigliato.

## Esempi rapidi

```text
Modello consigliato: GPT-5.4 mini
Motivo: aggiorniamo solo documentazione e verifichiamo il diff.
```

```text
Modello consigliato: GPT-5.4
Motivo: fix circoscritto in un modulo con test di regressione mirato.
```

```text
Modello consigliato: GPT-5.5
Motivo: il bug attraversa GUI, worker, rete e gestione asincrona.
```
