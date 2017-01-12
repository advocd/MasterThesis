#README

Weitere Informationen befinden sich als Kommentare in den jeweilen Dateien
sowie in dem Kapitel „Implementierung“ der Masterarbeit.

Bei dem hier vorliegenden Quellcode handelt es sich ausschließlich um Auszüge
aus Pery und ist in dieser Form nicht lauffähig.

##Projekt Hierarchie:

\pery
    \erp
        \jobs
            Beinhaltet das Job-Skript um diverse Informationen zu berechnen
        \templates
            \admin
                \erp\trip\
                    Beinhaltet die modular aufgebauten Templates des Prototypen
                    (ausser das Template für die Map-View)
            \erp
                map.html
                    Beinhaltet das Template für die Map-View
        \utils
            \gis
                Beinhaltet die Basisimplementierung für die Karten- und Listenansicht
            \trip
                Beinhaltet die spezifische Implementierung für die Realisierung des
                Prototypens am Szenario der Außendienstplanung.