WinPackIt - il modo semplice per distribuire progetti Python su Windows.
========================================================================

WinPackIt è il modulo ``winpackit.py`` uno script Python script che non richiede pacchetti esterni per funzionare. Il suo compito è generare una distribuzione "portatile" del vostro progetto Python su Windows.

Come funziona.
--------------

Python 3.5 ha introdotto gli `embeddable package`_ per Windows: ovvero, un Python "quasi completo" zippato in un un file singolo, non installabile. Lo scopo principale dovrebbe essere aiutare chi desidera incorporare Python in un altro programma, ma è possibile fare anche il contrario. Con qualche accorgimento, si può convertire questo pacchetto in un ambiente Python completo e isolato, in grado di supportare l'esecuzione di un programma. 

In pratica, è proprio ciò che fa WinPackIt. 

Quando avviate WinPackIt, lui
    - scarica e scompatta un "embeddable package" di Python, 
    - scarica e ci installa dentro Pip, 
    - scarica e ci installa dentro qualsiasi pacchetto esterno richiesto, 
    - copia i file del vostro progetto, 
    - se volete li compila in ``.pyc``,
    - lascia un amichevole ``install.bat`` da far eseguire all'utente finale.

A questo punto, potete consegnare la directory "build" generata agli utenti: tutto ciò che devono fare è
    - lasciarla dove preferiscono nel loro computer, 
    - aprire la cartella e fare doppio clic su ``install.bat``,
    - cosa che a sua volta produce dei collegamenti Windows agli entry-point della vostra applicazione, già pronti all'uso. 

Che cosa *non* è WinPackIt.
---------------------------

WinPackIt *non* "compila" il vostro programma in qualche sorta di "eseguibile". Si limita a creare una directory con dentro Python e i file della vostra applicazione. Si tratta di un ambiente Python portatile, non di un eseguibile singolo. 

Inoltre WinPackIt non andrà oltre la sua directory "build", sul computer dell'utente: non scriverà nel Registro, non imposterà variabili d'ambiente, e così via. Voi potete, volendo, aggiungere del codice personalizzato per eseguire delle azioni al momento della "installazione" (ovvero, quando l'utente fa doppio clic su ``install.bat``). 

Infine tenete a mente che WinPackIt può installare qualsiasi pacchetto che si può installare con ``pip install`` su Windows, ma nient'altro. Per fortuna, ormai questo vuol dire il 99% delle cose. 

Avvertenza importante.
^^^^^^^^^^^^^^^^^^^^^^

WinPackIt è solo un po' di codice che svolge operazioni elementari sul file system (copia di file, avviare Pip con Subprocess, etc.). Non fa nessuna magia particolare, e non cerca di indovinare le vostre intenzioni. Occorre pur sempre da parte vostra l'attenzione di calibrare correttamente le impostazioni e capire che cosa succede dietro le quinte: se indicete un file che non c'è, oppure se il pacchetto che volete non è installabile, etc., WinPackIt non risolverà il problema per voi: il più delle volte si pianterà senza complimenti. Controllate sempre con attenzione l'output per accertarvi che tutto sia andato come volevate. Spesso è una buona idea impostare il livello di output di debug (``VERBOSE=2``).

Prerequisiti.
-------------

Occorre Python 3.6+ per usare WinPackIt sul vostro computer. Non c'è bisogno di nessun pacchetto esterno aggiuntivo.

Dal lato dell'utente finale, potete generare "build" basati su qualsiasi versione di Python dalla 3.5 in poi. Non è necessario che il vostro Python sia uguale a quello della "build": WinPackIt userà il Python della "build" per invocare ``pip install``, non il vostro. Quindi Pip troverà i pacchetti giusti per l'ambiente della distribuzione. S'intende che resta compito vostro verificare che il programma funzioni come previsto.

Se scegliete una distribuzione a 64 bit, considerate che gli utenti finali non potranno farla funzionare sul loro computer, se questo è a 32 bit. 

Utenti Linux/Mac/Windows 32 bit.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

WinPackIt funziona anche su Linux/Mac, naturalmente. Tuttavia, la sua routine prevede di invocare il Pyhton della distribuzione alcune volte per installare i pacchetti esterni e compilare i file ``.pyc``: e questo non è certamente possibile su Linux. Tuttavia, se non avete pacchetti esterni e non vi importa di compilare i file, WinPackIt dovrebbe funzionare senza problemi.

Ma anche se siete su Windows, l'architettura del sistema può essere un ostacolo. Potete scegliere tra distribuzioni a 32 e 64 bit: ma se voi avete Windows a 32 bit e scegliete una distribuzione a 64 bit, allora WinPackIt non sarà in grado di far funzionare il Python della distribuzione sul vostro computer, e quindi non potrà installare i pacchetti esterni né compilare i ``.pyc``. Di nuovo, potrebbe comunque funzionare se non avete bisogno di pacchetti esterni e non vi iporta di compilare i moduli. 

Ma se invece *avete* bisogno di installare pacchetti esterni, potete impostare l'opzione ``DELAYED_INSTALL`` (vedi sotto): così lasciate il compito di far girare il Python della distribuzione solo a "install time", sulla macchina dell'utente finale. In questo modo potete sfruttare fino in fondo WinPackiIt anche su Linux/Mac (o su Windows a 32 bit, se volete produrre una distribuzione a 64 bit).

In ogni caso, tenete presente che anche se siete in grado di generare una distribuzione Windows su una macchina Linux, certamente non potrete testarla dopo. 

Una nota su Tkinter.
^^^^^^^^^^^^^^^^^^^^

A proposito di prerequisiti, tenete a mente che gli "embeddable packages" di Python *non* includono Tkinter (né Idle a maggior ragione). E siccome Tkinter *non* è su PyPI, non potete semplicemente installarlo con ``pip install`` nella vostra distribuzione di WinPackIt. Forse in futuro troverò una soluzione... ma per il momento, se il vostro programma è basato su Tkinter non c'è niente da fare. 

(Opinione personale: davvero, siamo nel 2020 e Tkinter non è su PyPI. C'è bisogno di aggiungere altro? Forse è davvero il momento che vi facciate un regalo e passiate a un GUI framework più serio.)

Una nota su Python 2.7.
^^^^^^^^^^^^^^^^^^^^^^^

Smettete di usare Python 2.7, a partire da adesso.

A parte tutto, WinPackIt non funziona con un Python più vecchio di 3.6. Potete senz'altro modificare il codice sorgente e renderlo compatibile con le versioni precedenti. Ma anche così, non sareste comunque in grado di produrre distribuzioni compatibili con Python precedenti a 3.5.0, perché non ci sono "embeddable packages" disponibili da cui partire.

Quindi no, non potete usare WinPackIt per distribuire il vostro programma basato su Python 2.7.

Come si usa.
------------

Detto in breve: 
    - ``pip install winpackit`` nel vostro virtual environment, o magari ``pipx install winpackit`` se davvero vi piace WinPackIt e volete averlo sempre sottomano;
    - invocate ``python -m winpackit my_runner.py``;
    - questo produce un "runner" ``my_runner.py`` per WinPackIt: apritelo e modificatelo secondo le vostre esigenze;
    - invocate ``python my_runner.py``;
    - questo produce una directory "build" per il vostro progetto, secondo le indicazioni del "runner", pronta per essere consegnata all'utente finale.

Adesso, scendiamo più nel dettaglio.

Installazione.
--------------

WinPackIt è uno script stand-alone che non richiede altri pacchetti esterni. Potete installarlo con Pip (``pip install winpackit``, nel vostro Python di sistema o dentro un virtual environment). Oppure potete installarlo con Pipx (``pipx install winpackit``) se volete poterlo invocare da tutti i vostri environments.

O ancora, potete semplicemente scaricare lo script e metterlo dove preferite. Ricordate solo che il modulo ``winpackit.py`` sarà *importato* dal modulo "runner" che dovete generare: accertatevi di lasciarlo dove il "runner" possa trovarlo (in genere, nella stessa directory).

Generare lo script "runner".
----------------------------

Invocate ``python -m winpackit <my_runner.py>``, dove ``<my_runner.py>`` è il percorso (assoluto o relativo) dello script "runner". Se non indicate un nome, WinPackIt produrrà un file ``run_winpackit.py`` nella vostra directory corrente. 

Il "runner" è un template che potete personalizzare. La sua funzione è descrivere il vostro progetto da distribuire: dovreste includere il "runner" nella directory *root* del vostro progetto. Potete anche avere più di un "runner" per lo stesso progetto, in modo da generare distribuzioni differenti (per esempio basate su Python differenti).

Se state importando ``winpackit.py`` (per esempio perché state scrivendo il vostro *packager* personalizzato), allora chiamate ``winpackit.make_runner_script(namefile)`` per produrre un "runner" script ``namefile``. 

Personalizzare lo script "runner".
----------------------------------

Qui è dove accade tutto. Aprite il "runner" con il vostro editor e riempite le varie impostazioni, a seconda dell'ambiente specifico del vostro progetto. Lo script include alcuni commenti utili a orientarvi. Esaminiamo le diverse impostazioni una per una.

``VERBOSE``
^^^^^^^^^^^

Impostate a ``1`` per il normale output, o ``2`` se ne volete un po' di più. Non è consigliabile impostarlo a ``0`` (muto).

``USE_CACHE``
^^^^^^^^^^^^^

WinPackIt mantiene una cache dei pacchetti scaricati in una directory ``winpackit_cache``. Se questa impostazione è ``True``, allora WinPackIt cercherà prima tra gli elementi scaricati in precedenza, facendovi risparmiare tempo di connessione.

``PYTHON_VERSION``
^^^^^^^^^^^^^^^^^^

Questa è la versione del Python della vostra distribuzione. Lasciate ``3`` per avere la più recente, o impostatela a una versione minore (per es. ``3.7``) per puntare alla più recente di quella serie, o ancora scegliete una versione specifica (``3.7.4``). Potete aggiungere ``-32`` o ``-64`` per specificare l'architettura del sistema (per es. ``3.7.4-32``). Il default è 64 bit. 

Un valore non valido (o vuoto) punterà alla versione del *vostro* Python attuale. Se il vostro Python non ha un "embeddable package" su cui basare la distribuzione, ``PYTHON_VERSION`` sarà ``3.5`` di default. Ricordiamo che non sono disponibili "embeddable package" prima della versione ``3.5.0``. 

**Nota**: inoltre non sono disponibili "embeddable package" per le release "security fix" ``3.5.5+`` e ``3.6.9+``.

``DELAYED_INSTALL``
^^^^^^^^^^^^^^^^^^^

Se impostato, produce una "installazione ritardata" sulla macchina dell'utente finale. WinPackIt non installerà pacchetti esterni e non compilerà i file ``.pyc`` nella vostra directory "build": invece, lascerà le istruzioni necessarie per svolgere questi compiti sulla macchina dell'utente. In questo modo, il Python della distribuzione non dovrà mai essere avviato da WinPackIt sulla vostra macchina.

Impostate questa opzione se siete su Linux/Mac, dal momento che l'eseguibile (Windows) di Python semplicemente non può funzionare sul vostro computer. Inoltre, impostate questa opzione se siete su Windows a 32 bit e volete produrre una distribuzione a 64 bit. 

Se non c'è bisogno di pacchetti esterni né di compilare i ``.pyc`` (vedi le opzioni ``PIP_REQUIRED``, ``REQUIREMENTS``, ``DEPENDENCIES`` e ``COMPILE`` qui sotto), allora questa impostazione non avrà effetto. 

``PIP_REQUIRED``
^^^^^^^^^^^^^^^^

Se è ``False`` Pip *non* sarà installato nella vostra distribuzione. Questo è utile se non avete bisogno di pacchetti esterni.

``REQUIREMENTS``
^^^^^^^^^^^^^^^^

Il percorso (assoluto o relativo a questo file "runner") di un file ``requirements.txt`` standard per Pip. Questo file è passato a Pip così com'è, senza nessun controllo da parte di WinPackIt. Se avete dei pacchetti "fissati", controllate che si accordino con la ``PYTHON_VERSION`` che avete impostato. 

``DEPENDENCIES``
^^^^^^^^^^^^^^^^

Una lista (di stringhe) di pacchetti esterni richiesti, da installare con Pip. Ogni string sarà passata a ``pip install`` così com'è: potete usare tutti i qualificatori di versione supportati da Pip. 

Potete impostare ``DEPENDENCIES`` e/o ``REQUIREMENTS`` come preferite. Se li impostate entrambi, allora ``REQUIREMENTS`` sarà processato per primo.

``PIP_CACHE``
^^^^^^^^^^^^^

Se impostato, WinPackIt userà la sua cache (almeno, se avete impostato ``USE_CACHE``) come cache per Pip. Altrimenti, l'opzione ``--no-cache`` sarà passata all'eseguibile di Pip. 

``PIP_ARGS``
^^^^^^^^^^^^

Una lista di opzioni generali da passare a Pip. Consultate la documentazione di Pip per la lista delle opzioni disponibili. Notate che se ``VERBOSE=0``, l'opzione ``-qqq`` sarà passata di default. Inoltre, ``--no-cache`` sarà passata se ``PIP_CACHE=False``.

``PIP_ISTALL_ARGS``
^^^^^^^^^^^^^^^^^^^

Una lista di opzioni specifiche da passare a ``pip install``. Consultate la documentazione di Pip per la lista delle opzioni disponibili.

Considerate che alcune opzioni ``PIP_ARGS`` e ``PIP_INSTALL_ARGS`` potrebbero essere in conflitto con le procedure di WinPackIt. Queste due impostazioni sono messe a disposizione solo come supporto per gli utenti esperti. La cosa migliore è in genere lasciarle vuote. Se le usate, controllate bene l'output di WinPackIt.

``PROJECTS``
^^^^^^^^^^^^

Una lista di liste, che contiene i dati dei vostri progetti e relativi entry point. Un "progetto" in pratica è una directory: WinPackIt la copierà nella directorory di destinazione della distribuzione. Un "entry point" è un file sul quale l'utente può fare doppio clic: WinPackIt genera un collegamento Windows per questi. 

Di solito avete un singolo progetto con un singolo entry point, per esempio::

    PROJECTS = [
                ['path/to/my_project', ('main.py', 'Run My Program')],
               ]

Il primo elemento è il percorso alla directory del progetto: può essere una path assoluta o relativa allo script "runner". La directory del progetto sarà copiata al livello superiore della directory "build", quindi: ``winpackit_build_<timestamp>/my_project``. La directory del progetto può contenere quello che volete: ovviamente saranno per lo più moduli e package Python. Se volete escludere dei file o sotto-directory dalla copia, potete usare ``PROJECT_FILES_IGNORE_PATTERNS`` che vedremo tra poco.

Il secondo elemento della lista è una tupla, che contiene esattamente due stringhe. La prima è la path al file entry-point: *deve* essere relativa alla directory del progetto. La seconda è un nome che WinPackIt userà per il collegamento Windows (qui, ``Run My Program.lnk``). 

Questa è forse la configurazione più semplice. Adesso vediamo un esempio più complesso::

    PROJECTS = [
        ['path/to/my_project', ('main.pyw', 'My GUI Program'), 
                               ('utils/cleanup.py', 'Maintenance Routine'), 
                               ('docs/docs.pdf', 'Documentation')],
        ['to/other_project', ('main.py', 'My Other Program!'),
                             ('readme.txt', 'Readme')],
        ['to/various_utils'],
               ]

Questa configurazione mostra alcune opzioni ulteriori. In primo luogo, potete inserire quanti "progetti" volete dentro una distribuzione di WinPackIt. Può essere un modo di distribuire insieme diversi programmi scorrelati. Tuttavia, tenete a mente che WinPackIt aggiungerà ciascun progetto alla ``sys.path`` di Python: approfondiremo la questione tra poco.

Potete avere anche più di un entry-point: WinPackIt produrrà un collegamento per ciascuno. Se lo entry-point è un modulo Python (``.py`` o ``.pyw``), il collegamento lo associerà all'eseguibile corretto (``python.exe`` o ``pythonw.exe``). Gli altri tipi di file saranno passati a ``ShellExecuteEx``, lasciando così a Windows il compito di trovare il programma più adatto per aprirli. 

Infine, potete anche includere un progetto senza alcun entry-point. Siccome WinPackIt lo aggiungerà comunque alla ``sys.path``, questo potrà essere importato dagli altri progetti nella stessa distrubuzione. Si noti che questo di solito è considerato cattivo design: ne riparleremo in dettaglio tra poco.

``PROJECT_FILES_IGNORE_PATTERNS``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

WinPackIt usa ``shutils.copytree`` per copiare i vostri progetti: potete passare una lista di ``shutils.ignore_patterns`` per escludere file e/o directory non desiderate. Si noti che ``__pycache__`` è sempre aggiunta per default alla lista delle esclusioni.

``COMPILE``
^^^^^^^^^^^

Se impostato, WinPackIt compilerà i vostri moduli in file ``.pyc``.

``PYC_ONLY_DISTRIBUTION``
^^^^^^^^^^^^^^^^^^^^^^^^^

Se impostato, WinPackIt rimuoverà inoltre i file ``.py`` originali dalla distribuzione, producendo una famigerata "pyc-only distribution" offuscata. Siate consapevoli che questo è comunque uno dei modi più deboli per proteggere il vostro codice. 

Se impostate questa opzione, anche i moduli entry-point saranno compilati e rimossi. Tuttavia WinPackIt ricorderà l'estensione originale (``.py`` o ``.pyw``) e associerà anche i moduli compilati al corrispondente eseguibile Python. 

Se avete selezionato una "installazione ritardata" (vedi l'opzione ``DELAYED_INSTALL`` qui sopra), allora la "pyc-only distribution" sarà ancora più vulnerabile del solito. I file ``.py`` originali *devono* essere inclusi nella distribuzione, per poterli compilare sulla macchina dell'utente. In seguito WinPackIt li cancellerà, ma basta solo che l'utente li apra e li esamini *prima* di avviare il file batch ``install.bat`` per completare l'installazione.

``COPY_DIRS``
^^^^^^^^^^^^^

Una lista di directory aggiuntive, non-Python, da copiare nella distribuzione. Usate lo stesso formato e regole di ``PROJECT``. L'unica differenza è che WinPackIt non aggiungerà queste directory alla ``sys.path`` di Python.

Questa impostazione serve a includere nella distribuzione qualsiasi materiale aggiuntivo, per esempio la documentazione::

    COPY_DIRS = [
                 ['path/to/docs', ('index.html', 'Documentation')],
                ]

``custom_action``
^^^^^^^^^^^^^^^^^

Scrivete qui eventuale codice vostro, che volete che sia eseguito al termine del processo di packaging. Da questa funzione potete accedere agli elementi interni dell'istanza di ``winpackit.Packit`` che è il cuore di WinPackIt... ma avrete bisogno di studiare un poco il codice sorgente per questo.

Avviare lo script "runner".
---------------------------

Quando avete personalizzato il "runner", potete avviarlo con ``python my_runner.py``. 

Lo script produrrà una directory marcata con data e ora ``winpackit_build_<timestamp>``, contenente il vostro progetto pronto per essere distribuito.

Azioni post-deploy.
-------------------

Se adesso aprite la directory "build", vedrete che WinPackIt ha lasciato uno script Python ``winpackit_bootstrap/bootstrap.py`` che l'utente finale deve eseguire per completare l'installazione sulla sua macchina. Questo script sarà avviato facendo doppio clic su un comodo ``install.bat`` che potete vedere nella directory "build".

Questo script di avvio produce i collegamenti Windows che avete elencato nelle impostazioni ``PROJECTS`` e ``COPY_DIRS`` viste sopra. I collegamenti *devono* essere creati sul computer dell'utente, perché la loro configurazione dipende dal file system locale.

Se avete selezionato una "installazione ritardata" (vedi l'opzione ``DELAYED_INSTALL`` qui sopra), allora lo script di avvio si occuperà anche di scaricare e installare i pacchetti esterni necessari e/o di compilare i file ``.pyc``. Se qualcosa va storto, dite all'utente di mandarvi il file di log ``winpackit_bootstrap/install.log`` e ispezionatelo. 

Potete approfittarne per aggiungere delle azioni post-deploy personalizzate nel modulo Python di bootstrap. Ricordate solo che questo codice verrà eseguito sulla macchina dell'utente, non sulla vostra: accordate bene le vostre path.

Testare la distribuzione.
-------------------------

Per testare la distribuzione, agite come farebbe l'utente finale. Spostare/rinominate la directory di "build", apritela e fate doppio clic su ``install.bat``. Questo produrrà i collegamenti necessari, nella stessa directory. Potete spostarli liberamente dove volete (di solito, sul desktop!). Quando fate doppio clic sul collegamento all'entry-point principale, il vostro programma dovrebbe avviarsi. 

Se rinominate/muovete ancora la directory "build", i collegamenti smetteranno naturalmente di funzionare. Buttateli via e generatene di nuovi avviando ancora ``install.bat``. 

Isolamento e "import".
----------------------

L'obiettivo di WinPackIt è produrre distribuzioni *stand-alone*, ovvero non solo auto-contenute ma anche *isolate* da ogni altro Python che potrebbe essere installato (magari anche in futuro) sulla macchina dell'utente. Di conseguenza WinPackIt non usa il consueto meccanismo di Python (il modulo ``site.py``) per riempire la ``sys.path`` e avviare il meccanismo degli "import". WinPackIt preferisce invece affidarsi a un file top-level``pythonXX._pth`` per aggiungere manualmente path alla ``sys.path``. Non usando ``site.py``, WinPackIt taglia fuori dalla ``sys.path`` ogni ``PATH``, ``PYTHONPATH`` etc. che potrebbe essere presente sul sistema ospite.

WinPackIt elenca *tutte* le vostre directory ``PROJECTS`` nel file ``pythonXX._pth`` come appena detto. Dovete capire comunque che questo design è utile ma anche pericoloso. Lo scenario "corretto" è avere un solo progetto "principale", ed eventualmente una o più directory "secondarie" che contengono strumenti che avete bisogno di importare, ma che non potete installare con Pip. Questo emula il comportamento di ``PYTHONPATH`` o anche della PEP 370 ("per user site-packages directory"). 

Tuttavia dovete comprendere che i meccanismi di ``PYTHONPATH``/PEP 370 sono pensati più per accogliere strumenti comuni *di sviluppo* che non pacchetti necessari all'ambiente di produzione. Di conseguenza, anche se WinPackIt supporta questa strategia di avere più di un ``PROJECTS``, non la incoraggia nemmeno. Il design migliore resta di avere esattamente *un* solo progetto auto-contenuto, e installare con Pip tutti i pacchetti necessari. 

Il design peggiore è invece includere diversi progetti non correlati tra loro nella stessa distribuzione (al contrario di avere, per lo meno, un solo progetto e diversi tool da importare). A questo punto ciascun progetto "vede" anche gli altri nella sua ``sys.path`` e voi dovete stare molto attenti a possibili "name shadowing". La cosa migliore è non farlo: se avete diversi progetti, create una distribuzione separata di WinPackIt per ciascuno. 

Supporto per Python 3.5.
^^^^^^^^^^^^^^^^^^^^^^^^

Python 3.5 non supporta i file ``._pth``. Per ragioni di consistenza con il modo in cui sono trattate le altre versioni di Python, WinPackIt aggiunge lo stesso tutte le directory ``PROJECTS`` a ``sys.path``, usando però un modulo ``sitecustomize.py``. In questo modo però ``site.py`` *sarà* importato, e di conseguenza la vostra distribuzione *potrebbe* essere meno isolata dall'ambiente circostante. 

Codice sorgente, esempi, test.
------------------------------

Il codice di ``winpackit.py`` è abbastanza lineare, anche se non sempre ben documentato. Se avete bisogno di studiarlo, potete iniziare dalla funzione ``Packit.main``, che elenca le varie operazioni che sono eseguite in successione nel corso di una tipica sessione di "build".

La repository GitHub ha alcuni esempi di progetti che possono essere trattati con WinPackIt: la suite di test li "impacchetta" con varie configurazioni. 


.. _embeddable package: https://docs.python.org/3/using/windows.html#the-embeddable-package
