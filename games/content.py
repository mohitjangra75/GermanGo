"""Cities for the Germany map quiz.

Easy cities come first so the opening question is winnable. Coordinates
are normalised: x runs -1 (west) to 1 (east), z runs -1 (north) to 1
(south). Berlin sits at roughly (0.42, -0.42).
"""

from __future__ import annotations

from dataclasses import dataclass

from django.utils.text import slugify

EASY, MEDIUM, HARD = 1, 2, 3


@dataclass(frozen=True)
class City:
    name: str
    state: str
    x: float
    z: float
    difficulty: int
    population: int
    color: str
    hint: str
    fact: str
    phrase: str = ""
    phrase_en: str = ""

    @property
    def slug(self) -> str:
        return slugify(self.name)

    def as_payload(self) -> dict:
        """The compact shape the Three.js scene and the quiz need."""
        return {
            "slug": self.slug,
            "name": self.name,
            "state": self.state,
            "x": self.x,
            "z": self.z,
            "color": self.color,
            "hint": self.hint,
            "fact": self.fact,
            "phrase": self.phrase,
            "phraseEn": self.phrase_en,
            "difficulty": self.difficulty,
        }


CITIES = [
    City("Berlin", "Berlin", 0.42, -0.42, EASY, 3850809, "#C0261A",
         hint="In the north-east, closer to Poland than to the Rhine.",
         fact="Berlin has more bridges than Venice — around 1,700 of them.",
         phrase="Ich hätte gern einen Kaffee.", phrase_en="I would like a coffee."),
    City("Munich", "Bayern", 0.18, 0.62, EASY, 1512491, "#2A6F52",
         hint="Deep in the south, with the Alps an hour away.",
         fact="The Oktoberfest mostly happens in September.",
         phrase="Grüß Gott!", phrase_en="Hello! (southern greeting)"),
    City("Hamburg", "Hamburg", 0.04, -0.66, EASY, 1892122, "#2F5D8C",
         hint="The great northern port, on the Elbe.",
         fact="Hamburg's Speicherstadt is the largest warehouse district in the world.",
         phrase="Moin!", phrase_en="Hello! (northern, any time of day)"),
    City("Cologne", "Nordrhein-Westfalen", -0.54, 0.06, EASY, 1073096, "#B98600",
         hint="West, on the Rhine, with the twin-spired cathedral.",
         fact="Cologne Cathedral took 632 years to finish.",
         phrase="Kölle Alaaf!", phrase_en="The Cologne carnival cry"),
    City("Frankfurt", "Hessen", -0.30, 0.20, EASY, 773068, "#E63329",
         hint="Centre-west: the skyline of banks and the busiest airport.",
         fact="Frankfurt Airport connects to more countries than any other.",
         phrase="Sprechen Sie Englisch?", phrase_en="Do you speak English?"),
    City("Stuttgart", "Baden-Württemberg", -0.22, 0.52, MEDIUM, 630305, "#7A4B9C",
         hint="South-west, in a valley surrounded by vineyards.",
         fact="Both Mercedes-Benz and Porsche were founded here.",
         phrase="Wo ist der Bahnhof?", phrase_en="Where is the train station?"),
    City("Dresden", "Sachsen", 0.52, 0.02, MEDIUM, 556227, "#2A6F52",
         hint="East, on the Elbe, near the Czech border.",
         fact="Dresden's Frauenkirche was rebuilt from its own rubble.",
         phrase="Wie viel kostet das?", phrase_en="How much does that cost?"),
    City("Leipzig", "Sachsen", 0.36, -0.06, MEDIUM, 601866, "#CA6702",
         hint="East-central, an hour or so north-west of Dresden.",
         fact="Bach worked at the Thomaskirche here for 27 years.",
         phrase="Ich verstehe nicht.", phrase_en="I do not understand."),
    City("Düsseldorf", "Nordrhein-Westfalen", -0.58, -0.04, MEDIUM, 619294, "#2F5D8C",
         hint="West, on the Rhine, just north of Cologne.",
         fact="It has the largest Japanese community in Germany.",
         phrase="Können Sie mir helfen?", phrase_en="Can you help me?"),
    City("Bremen", "Bremen", -0.14, -0.56, HARD, 566573, "#B98600",
         hint="North-west, inland from the coast on the Weser.",
         fact="The Bremen Town Musicians never actually reach Bremen in the tale.",
         phrase="Entschuldigung!", phrase_en="Excuse me!"),
    City("Nuremberg", "Bayern", 0.16, 0.36, HARD, 518370, "#C0261A",
         hint="Northern Bavaria, between Frankfurt and Munich.",
         fact="Its Christkindlesmarkt is the most famous Christmas market in Germany.",
         phrase="Frohe Weihnachten!", phrase_en="Merry Christmas!"),
    City("Hanover", "Niedersachsen", -0.08, -0.32, HARD, 535932, "#7A4B9C",
         hint="North-central, on the route between Berlin and the Ruhr.",
         fact="The clearest standard German is often said to be spoken here.",
         phrase="Sprechen Sie langsamer, bitte.", phrase_en="Please speak more slowly."),
]
