graph LR
    subgraph SuperSuperHirn
        UC1(Code setzen)
        UC2(Farben raten)
        UC3(Zeitlimit beachten)
    end

    Spieler((Spieler))
    Bot((Bot/System))

    Spieler --- UC2
    Spieler --- UC3
    Bot --- UC1
    Bot --- UC2