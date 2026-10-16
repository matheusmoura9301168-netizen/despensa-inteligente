"""
Migrações de base de dados: criação de tabelas e seed de 20 receitas.
"""
from app.database.connection import get_connection, release_connection

# ---------------------------------------------------------------------------
# DDL — Criação de Tabelas
# ---------------------------------------------------------------------------
CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS pantry_items (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    quantity   DECIMAL(10,2) NOT NULL DEFAULT 1,
    unit       VARCHAR(30)  NOT NULL DEFAULT 'unidades',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recipes (
    id           SERIAL PRIMARY KEY,
    title        VARCHAR(200) NOT NULL,
    description  TEXT,
    category     VARCHAR(50),
    difficulty   VARCHAR(20) DEFAULT 'Médio',
    prep_time    INTEGER DEFAULT 0,
    cook_time    INTEGER DEFAULT 0,
    servings     INTEGER DEFAULT 4,
    instructions TEXT
);

CREATE TABLE IF NOT EXISTS recipe_ingredients (
    id              SERIAL PRIMARY KEY,
    recipe_id       INTEGER REFERENCES recipes(id) ON DELETE CASCADE,
    ingredient_name VARCHAR(100) NOT NULL,
    quantity        DECIMAL(10,2),
    unit            VARCHAR(30),
    optional        BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_pantry_name ON pantry_items(LOWER(name));
CREATE INDEX IF NOT EXISTS idx_ri_recipe   ON recipe_ingredients(recipe_id);
"""

# ---------------------------------------------------------------------------
# Seed — 20 Receitas (Misto: Português + Internacional)
# ---------------------------------------------------------------------------
RECIPES_SEED = [
    # ── Receitas Portuguesas ──────────────────────────────────────────────
    {
        "title": "Bacalhau à Brás",
        "description": "Clássico português com bacalhau desfiado, batata palha crocante e ovos mexidos cremosos.",
        "category": "Prato Principal",
        "difficulty": "Médio",
        "prep_time": 20,
        "cook_time": 25,
        "servings": 4,
        "instructions": (
            "1. Demolhe o bacalhau de véspera, trocando a água várias vezes. Escorra e desfie em lascas.\n"
            "2. Descasque e corte as cebolas em meias-luas finas.\n"
            "3. Aqueça o azeite numa frigideira larga e refogue a cebola e o alho em lume médio até dourar.\n"
            "4. Adicione o bacalhau desfiado e salteie por 3 minutos, mexendo com frequência.\n"
            "5. Junte a batata palha e misture bem com o bacalhau.\n"
            "6. Bata os ovos com sal e pimenta. Adicione à mistura e mexa em lume baixo.\n"
            "7. Retire do lume quando os ovos estiverem cremosos (não totalmente cozidos).\n"
            "8. Sirva decorado com salsa fresca picada e azeitonas pretas."
        ),
        "ingredients": [
            ("bacalhau desfiado", 400, "g", False),
            ("batata palha", 200, "g", False),
            ("ovos", 4, "unidades", False),
            ("cebola", 2, "unidades", False),
            ("alho", 3, "dentes", False),
            ("azeite", 4, "colheres de sopa", False),
            ("salsa", 1, "ramo", True),
            ("azeitonas pretas", 50, "g", True),
            ("sal", 1, "pitada", False),
            ("pimenta preta", 1, "pitada", False),
        ],
    },
    {
        "title": "Caldo Verde",
        "description": "Sopa tradicional portuguesa com couve-galega, linguiça e batata cremosa.",
        "category": "Sopa",
        "difficulty": "Fácil",
        "prep_time": 15,
        "cook_time": 30,
        "servings": 6,
        "instructions": (
            "1. Descasque e corte as batatas em cubos. Pique a cebola e o alho grosseiramente.\n"
            "2. Num tacho, aqueça o azeite e refogue a cebola e o alho por 5 minutos.\n"
            "3. Adicione as batatas e cubra com água ou caldo. Cozinhe até as batatas ficarem macias.\n"
            "4. Triture a sopa com varinha mágica até ficar cremosa.\n"
            "5. Junte a linguiça cortada em rodelas e deixe ferver 5 minutos.\n"
            "6. Adicione a couve-galega cortada em juliana fina e cozinhe mais 3-4 minutos.\n"
            "7. Tempere com sal e regue com azeite antes de servir."
        ),
        "ingredients": [
            ("couve-galega", 300, "g", False),
            ("batata", 4, "unidades", False),
            ("linguiça", 150, "g", False),
            ("cebola", 1, "unidades", False),
            ("alho", 2, "dentes", False),
            ("azeite", 3, "colheres de sopa", False),
            ("sal", 1, "pitada", False),
            ("caldo de legumes", 1500, "ml", True),
        ],
    },
    {
        "title": "Frango Assado com Batatas",
        "description": "Frango assado no forno com batatas e alho, marinado em vinho branco e pimentão.",
        "category": "Prato Principal",
        "difficulty": "Médio",
        "prep_time": 20,
        "cook_time": 75,
        "servings": 4,
        "instructions": (
            "1. Misture o alho picado, pimentão doce, sumo de limão, azeite, sal e pimenta.\n"
            "2. Barre o frango com esta mistura por dentro e por fora. Marine 30 minutos.\n"
            "3. Pré-aqueça o forno a 200°C.\n"
            "4. Coloque o frango numa assadeira. Regue com vinho branco.\n"
            "5. Descasque as batatas, corte em quartos e disponha à volta do frango.\n"
            "6. Tempere as batatas com sal, azeite e pimentão.\n"
            "7. Leve ao forno por 75 minutos, regando o frango com o molho a cada 20 minutos.\n"
            "8. O frango está pronto quando a pele estiver dourada e crocante."
        ),
        "ingredients": [
            ("frango inteiro", 1500, "g", False),
            ("batata", 800, "g", False),
            ("alho", 6, "dentes", False),
            ("limão", 1, "unidades", False),
            ("azeite", 5, "colheres de sopa", False),
            ("vinho branco", 150, "ml", False),
            ("pimentão doce", 2, "colheres de chá", False),
            ("sal", 1, "pitada", False),
            ("pimenta preta", 1, "pitada", False),
        ],
    },
    {
        "title": "Arroz de Tomate",
        "description": "Acompanhamento simples e saboroso, com tomate fresco, cebola e azeite.",
        "category": "Acompanhamento",
        "difficulty": "Fácil",
        "prep_time": 5,
        "cook_time": 20,
        "servings": 4,
        "instructions": (
            "1. Pique a cebola e o alho finamente.\n"
            "2. Aqueça o azeite e refogue a cebola e o alho até ficarem translúcidos.\n"
            "3. Adicione o tomate picado (sem pele) e deixe refogar 5 minutos.\n"
            "4. Junte o arroz e mexa 1 minuto para tostar ligeiramente.\n"
            "5. Adicione água quente (o dobro do volume de arroz) e sal.\n"
            "6. Cozinhe em lume médio-baixo com tampa por 15-18 minutos.\n"
            "7. Retire do lume e deixe repousar 5 minutos antes de servir."
        ),
        "ingredients": [
            ("arroz", 300, "g", False),
            ("tomate", 3, "unidades", False),
            ("cebola", 1, "unidades", False),
            ("alho", 2, "dentes", False),
            ("azeite", 3, "colheres de sopa", False),
            ("sal", 1, "pitada", False),
            ("pimenta preta", 1, "pitada", False),
        ],
    },
    {
        "title": "Bifanas",
        "description": "Sanduíche portuguesa com carne de porco marinada em vinho e especiarias.",
        "category": "Lanche",
        "difficulty": "Fácil",
        "prep_time": 15,
        "cook_time": 15,
        "servings": 4,
        "instructions": (
            "1. Marine a carne de porco em vinho branco, alho picado, pimentão doce, louro, sal e pimenta por 1 hora (ou de véspera).\n"
            "2. Aqueça azeite ou banha numa frigideira em lume alto.\n"
            "3. Escorra a carne da marinada (guarde o líquido) e frite as bifanas em lume alto, 2-3 minutos de cada lado.\n"
            "4. Reduza o lume, adicione a marinada e deixe reduzir um pouco.\n"
            "5. Aqueça os pães ligeiramente.\n"
            "6. Sirva as bifanas dentro dos pães regadas com o molho."
        ),
        "ingredients": [
            ("carne de porco em bifanas", 500, "g", False),
            ("vinho branco", 200, "ml", False),
            ("alho", 4, "dentes", False),
            ("pimentão doce", 1, "colher de chá", False),
            ("louro", 2, "folhas", False),
            ("sal", 1, "pitada", False),
            ("pimenta preta", 1, "pitada", False),
            ("pão de bolo", 4, "unidades", False),
            ("azeite", 2, "colheres de sopa", False),
        ],
    },
    {
        "title": "Açorda Alentejana",
        "description": "Sopa de pão alentejana com ovos escalfados, coentros frescos e alho.",
        "category": "Prato Principal",
        "difficulty": "Fácil",
        "prep_time": 10,
        "cook_time": 15,
        "servings": 4,
        "instructions": (
            "1. Pique o alho e os coentros grosseiramente.\n"
            "2. Num almofariz, pise o alho com sal grosso até formar uma pasta.\n"
            "3. Corte o pão alentejano em fatias e distribua nos pratos fundos.\n"
            "4. Ferva água com o azeite e o alho pisado por 5 minutos.\n"
            "5. Escalde os ovos no líquido a ferver (3-4 minutos para gema mole).\n"
            "6. Retire os ovos e reserve.\n"
            "7. Verta o caldo quente por cima do pão para o embeber bem.\n"
            "8. Coloque os ovos escalfados por cima e salpique com coentros frescos.\n"
            "9. Regue com um fio de azeite e sirva imediatamente."
        ),
        "ingredients": [
            ("pão alentejano duro", 300, "g", False),
            ("ovos", 4, "unidades", False),
            ("alho", 4, "dentes", False),
            ("coentros", 1, "ramo", False),
            ("azeite", 5, "colheres de sopa", False),
            ("sal grosso", 1, "colher de chá", False),
        ],
    },
    {
        "title": "Arroz de Frango",
        "description": "Arroz caldoso com frango desfiado, refogado de cebola e especiarias.",
        "category": "Prato Principal",
        "difficulty": "Médio",
        "prep_time": 15,
        "cook_time": 40,
        "servings": 4,
        "instructions": (
            "1. Cozinhe o frango em água com sal, cebola e louro por 30 minutos. Reserve o caldo.\n"
            "2. Desfie o frango cozido e reserve.\n"
            "3. Refogue a cebola picada e o alho no azeite até dourar.\n"
            "4. Adicione o tomate picado e cozinhe 5 minutos.\n"
            "5. Junte o arroz e mexa 1 minuto.\n"
            "6. Adicione o caldo do frango quente (2,5x o volume do arroz).\n"
            "7. Adicione o frango desfiado e cozinhe em lume médio por 15 minutos.\n"
            "8. Tempere e sirva polvilhado com salsa picada."
        ),
        "ingredients": [
            ("frango", 600, "g", False),
            ("arroz", 300, "g", False),
            ("cebola", 1, "unidades", False),
            ("alho", 3, "dentes", False),
            ("tomate", 2, "unidades", False),
            ("azeite", 3, "colheres de sopa", False),
            ("louro", 1, "folha", False),
            ("sal", 1, "pitada", False),
            ("salsa", 1, "ramo", True),
        ],
    },
    {
        "title": "Sopa de Feijão com Chouriço",
        "description": "Sopa rica e reconfortante com feijão vermelho, chouriço e legumes.",
        "category": "Sopa",
        "difficulty": "Fácil",
        "prep_time": 10,
        "cook_time": 40,
        "servings": 6,
        "instructions": (
            "1. Se usar feijão seco, demolhe de véspera e coza por 40 minutos.\n"
            "2. Refogue a cebola e o alho picados no azeite até dourar.\n"
            "3. Adicione o chouriço cortado em rodelas e salteie 2 minutos.\n"
            "4. Adicione a cenoura em rodelas e a batata em cubos.\n"
            "5. Cubra com caldo e cozinhe por 20 minutos.\n"
            "6. Junte o feijão cozido e deixe ferver mais 10 minutos.\n"
            "7. Corrija o sal e sirva com pão rústico."
        ),
        "ingredients": [
            ("feijão vermelho", 400, "g", False),
            ("chouriço", 150, "g", False),
            ("cenoura", 2, "unidades", False),
            ("batata", 2, "unidades", False),
            ("cebola", 1, "unidades", False),
            ("alho", 2, "dentes", False),
            ("azeite", 3, "colheres de sopa", False),
            ("caldo de legumes", 1500, "ml", False),
            ("sal", 1, "pitada", False),
        ],
    },

    # ── Receitas Internacionais ───────────────────────────────────────────
    {
        "title": "Massa Bolonhesa",
        "description": "Clássico molho à bolonhesa com carne picada, tomate e ervas aromáticas.",
        "category": "Prato Principal",
        "difficulty": "Médio",
        "prep_time": 15,
        "cook_time": 45,
        "servings": 4,
        "instructions": (
            "1. Refogue a cebola e o alho no azeite até dourar.\n"
            "2. Adicione a carne picada e cozinhe em lume alto, partindo os pedaços, até tostar.\n"
            "3. Regue com o vinho tinto e deixe evaporar o álcool.\n"
            "4. Adicione o tomate pelado esmagado, o louro, sal e pimenta.\n"
            "5. Cozinhe em lume baixo por 30-40 minutos, mexendo ocasionalmente.\n"
            "6. Coza o esparguete em água a ferver com sal segundo as instruções da embalagem.\n"
            "7. Sirva a massa com o molho e polvilhe com parmesão ralado."
        ),
        "ingredients": [
            ("esparguete", 400, "g", False),
            ("carne picada", 500, "g", False),
            ("tomate pelado", 400, "g", False),
            ("cebola", 1, "unidades", False),
            ("alho", 3, "dentes", False),
            ("vinho tinto", 150, "ml", False),
            ("azeite", 3, "colheres de sopa", False),
            ("louro", 1, "folha", False),
            ("parmesão ralado", 50, "g", True),
            ("sal", 1, "pitada", False),
            ("pimenta preta", 1, "pitada", False),
        ],
    },
    {
        "title": "Risotto de Cogumelos",
        "description": "Risotto cremoso italiano com cogumelos frescos e parmesão.",
        "category": "Prato Principal",
        "difficulty": "Médio",
        "prep_time": 10,
        "cook_time": 35,
        "servings": 4,
        "instructions": (
            "1. Aqueça o caldo de legumes numa panela separada e mantenha quente.\n"
            "2. Refogue a cebola picada na manteiga até ficar translúcida.\n"
            "3. Adicione os cogumelos fatiados e o alho, e salteie 5 minutos.\n"
            "4. Junte o arroz arbóreo e mexa 1 minuto para tostar ligeiramente.\n"
            "5. Adicione o vinho branco e mexa até absorver.\n"
            "6. Adicione concha a concha o caldo quente, mexendo sempre e esperando absorver entre cada adição (20-25 min).\n"
            "7. Quando o arroz estiver al dente e cremoso, retire do lume.\n"
            "8. Misture a manteiga restante e o parmesão. Tempere e sirva."
        ),
        "ingredients": [
            ("arroz arbóreo", 320, "g", False),
            ("cogumelos", 300, "g", False),
            ("cebola", 1, "unidades", False),
            ("alho", 2, "dentes", False),
            ("vinho branco", 150, "ml", False),
            ("caldo de legumes", 1200, "ml", False),
            ("manteiga", 50, "g", False),
            ("parmesão ralado", 80, "g", False),
            ("sal", 1, "pitada", False),
            ("pimenta preta", 1, "pitada", False),
        ],
    },
    {
        "title": "Omelete de Queijo",
        "description": "Omelete fofa e dourada recheada com queijo derretido. Pronto em 10 minutos.",
        "category": "Pequeno-Almoço",
        "difficulty": "Fácil",
        "prep_time": 5,
        "cook_time": 8,
        "servings": 1,
        "instructions": (
            "1. Parta os ovos para uma tigela e bata com um garfo. Tempere com sal e pimenta.\n"
            "2. Derreta a manteiga numa frigideira antiaderente em lume médio.\n"
            "3. Adicione os ovos batidos. Deixe começar a solidificar nas bordas.\n"
            "4. Com uma espátula, puxe as bordas para o centro, inclinando a frigideira para os ovos líquidos preencherem.\n"
            "5. Quando a omelete estiver quase cozida (ainda um pouco húmida no centro), distribua o queijo ralado.\n"
            "6. Dobre a omelete ao meio com a espátula.\n"
            "7. Sirva imediatamente com pão torrado."
        ),
        "ingredients": [
            ("ovos", 3, "unidades", False),
            ("queijo", 50, "g", False),
            ("manteiga", 15, "g", False),
            ("sal", 1, "pitada", False),
            ("pimenta preta", 1, "pitada", False),
        ],
    },
    {
        "title": "Salada César",
        "description": "Salada clássica com alface romana, frango grelhado, croutons e molho César.",
        "category": "Entrada",
        "difficulty": "Fácil",
        "prep_time": 20,
        "cook_time": 15,
        "servings": 2,
        "instructions": (
            "1. Grelhe o peito de frango temperado com sal, pimenta e azeite por 6-7 minutos de cada lado.\n"
            "2. Deixe arrefecer e corte em fatias.\n"
            "3. Corte o pão em cubos e torre no forno com azeite a 180°C por 10 minutos.\n"
            "4. Lave e rasgue a alface romana em pedaços.\n"
            "5. Num bowl grande, misture a alface com o molho César.\n"
            "6. Adicione o frango fatiado, os croutons e o parmesão em lascas.\n"
            "7. Esprema um pouco de limão por cima e sirva de imediato."
        ),
        "ingredients": [
            ("alface romana", 1, "unidades", False),
            ("peito de frango", 200, "g", False),
            ("parmesão", 40, "g", False),
            ("pão", 2, "fatias", False),
            ("molho césar", 4, "colheres de sopa", False),
            ("limão", 1, "unidades", True),
            ("azeite", 2, "colheres de sopa", False),
            ("sal", 1, "pitada", False),
            ("pimenta preta", 1, "pitada", False),
        ],
    },
    {
        "title": "Frango à Parmesão",
        "description": "Peito de frango empanado coberto com molho de tomate e queijo mozzarella derretida.",
        "category": "Prato Principal",
        "difficulty": "Médio",
        "prep_time": 20,
        "cook_time": 25,
        "servings": 2,
        "instructions": (
            "1. Aplane os peitos de frango com um martelo de carne.\n"
            "2. Passe cada peito por farinha, depois em ovo batido, e por último em pão ralado.\n"
            "3. Frite no azeite bem quente, 3-4 minutos de cada lado, até dourar.\n"
            "4. Pré-aqueça o forno a 200°C.\n"
            "5. Coloque o frango frito numa assadeira, cubra com molho de tomate e queijo mozzarella fatiada.\n"
            "6. Polvilhe com parmesão ralado.\n"
            "7. Leve ao forno por 10-15 minutos até o queijo derreter e borbulhar.\n"
            "8. Sirva com massa ou salada verde."
        ),
        "ingredients": [
            ("peito de frango", 400, "g", False),
            ("farinha", 80, "g", False),
            ("ovos", 2, "unidades", False),
            ("pão ralado", 100, "g", False),
            ("molho de tomate", 200, "ml", False),
            ("queijo mozzarella", 150, "g", False),
            ("parmesão ralado", 50, "g", False),
            ("azeite", 4, "colheres de sopa", False),
            ("sal", 1, "pitada", False),
            ("pimenta preta", 1, "pitada", False),
        ],
    },
    {
        "title": "Guacamole",
        "description": "Molho mexicano cremoso com abacate, tomate, limão e coentros.",
        "category": "Entrada",
        "difficulty": "Fácil",
        "prep_time": 15,
        "cook_time": 0,
        "servings": 4,
        "instructions": (
            "1. Corte os abacates ao meio, retire o caroço e extraia a polpa.\n"
            "2. Esmague a polpa com um garfo (deixe um pouco texturizado).\n"
            "3. Pique o tomate em cubos pequenos (retire as sementes).\n"
            "4. Pique a cebola finamente.\n"
            "5. Misture o tomate, a cebola e os coentros picados com o abacate.\n"
            "6. Esprema o sumo de limão e tempere com sal e pimenta.\n"
            "7. Misture bem. Prove e ajuste o tempero.\n"
            "8. Sirva imediatamente com nachos ou palitos de legumes."
        ),
        "ingredients": [
            ("abacate", 2, "unidades", False),
            ("tomate", 1, "unidades", False),
            ("cebola", 0.5, "unidades", False),
            ("limão", 1, "unidades", False),
            ("coentros", 0.5, "ramo", False),
            ("sal", 1, "pitada", False),
            ("pimenta preta", 1, "pitada", False),
        ],
    },
    {
        "title": "Pizza Margherita",
        "description": "Pizza italiana clássica com molho de tomate, mozzarella e manjericão fresco.",
        "category": "Prato Principal",
        "difficulty": "Médio",
        "prep_time": 30,
        "cook_time": 25,
        "servings": 4,
        "instructions": (
            "1. Dissolva o fermento em água morna com 1 colher de açúcar. Aguarde 10 min.\n"
            "2. Numa tigela, misture a farinha com o sal. Adicione o fermento e o azeite.\n"
            "3. Amasse por 8-10 minutos até obter uma massa elástica. Tape e deixe levedar 1 hora.\n"
            "4. Pré-aqueça o forno à temperatura máxima (250°C+) com a pedra/tabuleiro dentro.\n"
            "5. Estenda a massa em círculo fino com rolo.\n"
            "6. Espalhe o molho de tomate, deixando 1 cm de borda.\n"
            "7. Distribua a mozzarella fatiada por cima.\n"
            "8. Leve ao forno por 10-12 minutos até a base estar crocante.\n"
            "9. Retire e coloque folhas de manjericão fresco por cima."
        ),
        "ingredients": [
            ("farinha de trigo", 400, "g", False),
            ("fermento seco", 7, "g", False),
            ("molho de tomate", 200, "ml", False),
            ("queijo mozzarella", 250, "g", False),
            ("manjericão", 1, "ramo", True),
            ("azeite", 3, "colheres de sopa", False),
            ("sal", 1, "colher de chá", False),
            ("açúcar", 1, "colher de chá", False),
        ],
    },
    {
        "title": "Sopa de Legumes",
        "description": "Sopa nutritiva e colorida com cenoura, batata e courgette.",
        "category": "Sopa",
        "difficulty": "Fácil",
        "prep_time": 10,
        "cook_time": 25,
        "servings": 4,
        "instructions": (
            "1. Descasque e corte a cenoura, a batata e a curgete em cubos.\n"
            "2. Pique a cebola e o alho.\n"
            "3. Aqueça o azeite e refogue a cebola e o alho por 3 minutos.\n"
            "4. Adicione a cenoura e a batata. Mexa e adicione o caldo.\n"
            "5. Cozinhe em lume médio por 15 minutos.\n"
            "6. Adicione a curgete e cozinhe mais 5 minutos.\n"
            "7. Triture parcialmente com varinha mágica (deixe alguns pedaços).\n"
            "8. Tempere com sal e pimenta. Sirva com pão."
        ),
        "ingredients": [
            ("cenoura", 3, "unidades", False),
            ("batata", 2, "unidades", False),
            ("courgette", 1, "unidades", False),
            ("cebola", 1, "unidades", False),
            ("alho", 2, "dentes", False),
            ("caldo de legumes", 1200, "ml", False),
            ("azeite", 2, "colheres de sopa", False),
            ("sal", 1, "pitada", False),
            ("pimenta preta", 1, "pitada", False),
        ],
    },
    {
        "title": "Panquecas",
        "description": "Panquecas fofas americanas, perfeitas para o pequeno-almoço com mel ou fruta.",
        "category": "Pequeno-Almoço",
        "difficulty": "Fácil",
        "prep_time": 10,
        "cook_time": 15,
        "servings": 4,
        "instructions": (
            "1. Misture a farinha, o fermento, o açúcar e o sal numa tigela.\n"
            "2. Noutro recipiente, bata os ovos com o leite e a manteiga derretida.\n"
            "3. Adicione os ingredientes líquidos aos secos e misture até ficar homogéneo (não bata em excesso).\n"
            "4. Aqueça uma frigideira antiaderente em lume médio-baixo com um pouco de manteiga.\n"
            "5. Deite uma concha de massa na frigideira e cozinhe até surgirem bolhas na superfície (2-3 min).\n"
            "6. Vire e cozinhe mais 1-2 minutos.\n"
            "7. Sirva com mel, xarope de ácer ou fruta fresca."
        ),
        "ingredients": [
            ("farinha", 200, "g", False),
            ("ovos", 2, "unidades", False),
            ("leite", 250, "ml", False),
            ("manteiga", 30, "g", False),
            ("açúcar", 30, "g", False),
            ("fermento em pó", 10, "g", False),
            ("sal", 1, "pitada", False),
        ],
    },
    {
        "title": "Brownie de Chocolate",
        "description": "Brownie denso e fudgy com chocolate negro e cacau. Uma sobremesa irresistível.",
        "category": "Sobremesa",
        "difficulty": "Médio",
        "prep_time": 15,
        "cook_time": 30,
        "servings": 12,
        "instructions": (
            "1. Pré-aqueça o forno a 175°C. Unte e forre uma forma retangular com papel vegetal.\n"
            "2. Derreta o chocolate negro e a manteiga em banho-maria ou microondas (em intervalos de 30s).\n"
            "3. Adicione o açúcar ao chocolate derretido e misture bem.\n"
            "4. Bata os ovos um a um na mistura.\n"
            "5. Adicione a farinha e o cacau em pó. Misture delicadamente até incorporar.\n"
            "6. Verta a massa na forma e alise a superfície.\n"
            "7. Leve ao forno por 25-30 minutos (o interior deve ficar úmido e húmido).\n"
            "8. Deixe arrefecer completamente antes de cortar em quadrados."
        ),
        "ingredients": [
            ("chocolate negro", 200, "g", False),
            ("manteiga", 115, "g", False),
            ("ovos", 3, "unidades", False),
            ("açúcar", 200, "g", False),
            ("farinha", 65, "g", False),
            ("cacau em pó", 30, "g", False),
        ],
    },
    {
        "title": "Wrap de Atum",
        "description": "Wrap rápido com atum, salada e maionese — refeição leve em 10 minutos.",
        "category": "Lanche",
        "difficulty": "Fácil",
        "prep_time": 10,
        "cook_time": 0,
        "servings": 2,
        "instructions": (
            "1. Escorra o atum e coloque numa tigela.\n"
            "2. Misture com a maionese e umas gotas de limão. Tempere com sal e pimenta.\n"
            "3. Lave e seque as folhas de alface. Corte o tomate em cubos.\n"
            "4. Disponha as folhas de alface na base da tortilha.\n"
            "5. Adicione o tomate em cubos sobre a alface.\n"
            "6. Espalhe o atum com maionese por cima.\n"
            "7. Enrole a tortilha de forma firme e corte ao meio na diagonal.\n"
            "8. Sirva imediatamente."
        ),
        "ingredients": [
            ("atum em lata", 160, "g", False),
            ("tortilha", 2, "unidades", False),
            ("alface", 50, "g", False),
            ("tomate", 1, "unidades", False),
            ("maionese", 2, "colheres de sopa", False),
            ("limão", 0.5, "unidades", True),
            ("sal", 1, "pitada", False),
            ("pimenta preta", 1, "pitada", False),
        ],
    },
    {
        "title": "Tacos de Frango",
        "description": "Tacos mexicanos com frango temperado, guacamole e salsa fresca.",
        "category": "Prato Principal",
        "difficulty": "Médio",
        "prep_time": 20,
        "cook_time": 15,
        "servings": 4,
        "instructions": (
            "1. Corte o frango em tiras. Tempere com cominho, pimentão, sal e pimenta.\n"
            "2. Grelhe o frango numa frigideira bem quente com azeite por 5-7 minutos até cozido.\n"
            "3. Aqueça as tortilhas diretamente na chama ou frigideira seca, 30 segundos de cada lado.\n"
            "4. Prepare a salsa: pique o tomate, a cebola e o coentro. Misture com sumo de limão.\n"
            "5. Monte os tacos: coloque alface, frango, salsa fresca e queijo ralado.\n"
            "6. Adicione creme azedo ou guacamole por cima.\n"
            "7. Sirva imediatamente com fatias de limão."
        ),
        "ingredients": [
            ("peito de frango", 500, "g", False),
            ("tortilha", 8, "unidades", False),
            ("alface", 100, "g", False),
            ("tomate", 2, "unidades", False),
            ("cebola", 0.5, "unidades", False),
            ("coentros", 0.5, "ramo", True),
            ("queijo ralado", 80, "g", True),
            ("creme azedo", 100, "ml", True),
            ("limão", 1, "unidades", False),
            ("cominho", 1, "colher de chá", False),
            ("pimentão", 1, "colher de chá", False),
            ("azeite", 2, "colheres de sopa", False),
            ("sal", 1, "pitada", False),
            ("pimenta preta", 1, "pitada", False),
        ],
    },
]


def run_migrations() -> None:
    """Cria tabelas e insere dados de seed se não existirem."""
    conn = get_connection()
    try:
        with conn:
            with conn.cursor() as cur:
                print("📋 A executar migrações...")
                cur.execute(CREATE_TABLES_SQL)
                print("✅ Tabelas criadas.")
                _seed_recipes(cur)
    finally:
        release_connection(conn)


def _seed_recipes(cur) -> None:
    """Insere receitas de exemplo se a tabela estiver vazia."""
    cur.execute("SELECT COUNT(*) FROM recipes")
    count = cur.fetchone()[0]
    if count > 0:
        print(f"📚 {count} receitas já existem na base de dados.")
        return

    print("🌱 A inserir receitas de exemplo...")
    for recipe in RECIPES_SEED:
        cur.execute(
            """
            INSERT INTO recipes
                (title, description, category, difficulty, prep_time, cook_time, servings, instructions)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                recipe["title"],
                recipe["description"],
                recipe["category"],
                recipe["difficulty"],
                recipe["prep_time"],
                recipe["cook_time"],
                recipe["servings"],
                recipe["instructions"],
            ),
        )
        recipe_id = cur.fetchone()[0]

        for ing in recipe["ingredients"]:
            cur.execute(
                """
                INSERT INTO recipe_ingredients
                    (recipe_id, ingredient_name, quantity, unit, optional)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (recipe_id, ing[0], ing[1], ing[2], ing[3]),
            )

    print(f"✅ {len(RECIPES_SEED)} receitas inseridas com sucesso!")
