// 1. Create Vector Indices (Run these one by one)

CREATE VECTOR INDEX book_index IF NOT EXISTS
FOR (b:Book) ON (b.embedding)
OPTIONS {indexConfig: {
  `vector.dimensions`: 384,
  `vector.similarity_function`: 'cosine'
}};

CREATE VECTOR INDEX author_index IF NOT EXISTS
FOR (a:Author) ON (a.embedding)
OPTIONS {indexConfig: {
  `vector.dimensions`: 384,
  `vector.similarity_function`: 'cosine'
}};

CREATE VECTOR INDEX genre_index IF NOT EXISTS
FOR (g:Genre) ON (g.embedding)
OPTIONS {indexConfig: {
  `vector.dimensions`: 384,
  `vector.similarity_function`: 'cosine'
}};

// 2. Create Genres
CREATE (g1:Genre {name: 'Fiction'})
CREATE (g2:Genre {name: 'Science Fiction'})
CREATE (g3:Genre {name: 'Thriller'})
CREATE (g4:Genre {name: 'Technology'})
CREATE (g5:Genre {name: 'Romance'})
CREATE (g6:Genre {name: 'Fantasy'})
CREATE (g7:Genre {name: 'Historical'})
CREATE (g8:Genre {name: 'Adventure'});

// 3. Create Authors
CREATE (a1:Author {name: 'Anna Morel'})
CREATE (a2:Author {name: 'Marcus Hill'})
CREATE (a3:Author {name: 'Laura Bennett'})
CREATE (a4:Author {name: 'Tom Reeves'})
CREATE (a5:Author {name: 'Sara Collins'})
CREATE (a6:Author {name: 'David Chen'})
CREATE (a7:Author {name: 'Layla Hunt'})
CREATE (a8:Author {name: 'Chris Nolan'})
CREATE (a9:Author {name: 'Rania Khaled'})
CREATE (a10:Author {name: 'Mina Gray'})
CREATE (a11:Author {name: 'Nora Avery'})
CREATE (a12:Author {name: 'James Porter'})
CREATE (a13:Author {name: 'Elena Marquez'})
CREATE (a14:Author {name: 'Lorena Diaz'})
CREATE (a15:Author {name: 'Sophie Turner'})
CREATE (a16:Author {name: 'Leo Harding'})
CREATE (a17:Author {name: 'Nadia Solis'})
CREATE (a18:Author {name: 'Alice Monroe'})
CREATE (a19:Author {name: 'Hector Ruiz'})
CREATE (a20:Author {name: 'Maya Winters'})
CREATE (a21:Author {name: 'Yassine Benali'})
CREATE (a22:Author {name: 'Hala Messaoud'})
CREATE (a23:Author {name: 'Ethan Clarke'})
CREATE (a24:Author {name: 'Robin Singh'})
CREATE (a25:Author {name: 'Emily Stone'})
CREATE (a26:Author {name: 'Adam Brooks'})
CREATE (a27:Author {name: 'Noah Parker'})
CREATE (a28:Author {name: 'Chloe Martin'})
CREATE (a29:Author {name: 'Tara Patel'})
CREATE (a30:Author {name: 'Julian Ross'})
CREATE (a31:Author {name: 'Dina Saidi'})
CREATE (a32:Author {name: 'Victor Adams'})
CREATE (a33:Author {name: 'Lina Torres'})
CREATE (a34:Author {name: 'Ziad Kamal'})
CREATE (a35:Author {name: 'Olivia Hale'})
CREATE (a36:Author {name: 'Nabil Jarrar'})
CREATE (a37:Author {name: 'Samira Haddad'})
CREATE (a38:Author {name: 'Jonas MÃ¼ller'})
CREATE (a39:Author {name: 'Anya Petrova'})
CREATE (a40:Author {name: 'Eric Lawson'})
CREATE (a41:Author {name: 'Mariam Azar'})
CREATE (a42:Author {name: 'Sami Harrak'})
CREATE (a43:Author {name: 'Helena Grayson'})
CREATE (a44:Author {name: 'Mohamed Idrissi'})
CREATE (a45:Author {name: 'Isabella Trent'})
CREATE (a46:Author {name: 'Arthur Kim'})
CREATE (a47:Author {name: 'Nadia Youssef'})
CREATE (a48:Author {name: 'Faris Alami'});

// 4. Create Books and Relationships
CREATE (b1:Book {title: 'The Silent Forest', year: 2018, pages: 324})
CREATE (b1)-[:BELONGS_TO]->(g1)
CREATE (a1)-[:WROTE]->(b1)

CREATE (b2:Book {title: 'Edge of Tomorrow', year: 2020, pages: 412})
CREATE (b2)-[:BELONGS_TO]->(g2)
CREATE (a2)-[:WROTE]->(b2)

CREATE (b3:Book {title: 'Hidden Truths', year: 2019, pages: 298})
CREATE (b3)-[:BELONGS_TO]->(g3)
CREATE (a3)-[:WROTE]->(b3)

CREATE (b4:Book {title: 'Digital Minds', year: 2021, pages: 265})
CREATE (b4)-[:BELONGS_TO]->(g4)
CREATE (a4)-[:WROTE]->(b4)

CREATE (b5:Book {title: 'Ocean Whispers', year: 2017, pages: 350})
CREATE (b5)-[:BELONGS_TO]->(g5)
CREATE (a5)-[:WROTE]->(b5)

CREATE (b6:Book {title: 'The Last Algorithm', year: 2022, pages: 410})
CREATE (b6)-[:BELONGS_TO]->(g4)
CREATE (a6)-[:WROTE]->(b6)

CREATE (b7:Book {title: 'City of Ashes', year: 2016, pages: 520})
CREATE (b7)-[:BELONGS_TO]->(g6)
CREATE (a7)-[:WROTE]->(b7)

CREATE (b8:Book {title: 'Mapping the Stars', year: 2015, pages: 389})
CREATE (b8)-[:BELONGS_TO]->(g2)
CREATE (a8)-[:WROTE]->(b8)

CREATE (b9:Book {title: 'Under the Olive Tree', year: 2014, pages: 312})
CREATE (b9)-[:BELONGS_TO]->(g7)
CREATE (a9)-[:WROTE]->(b9)

CREATE (b10:Book {title: 'Whispers at Midnight', year: 2021, pages: 275})
CREATE (b10)-[:BELONGS_TO]->(g3)
CREATE (a10)-[:WROTE]->(b10)

CREATE (b11:Book {title: 'Fragments of Light', year: 2020, pages: 330})
CREATE (b11)-[:BELONGS_TO]->(g1)
CREATE (a11)-[:WROTE]->(b11)

CREATE (b12:Book {title: 'The Quantum Key', year: 2023, pages: 450})
CREATE (b12)-[:BELONGS_TO]->(g2)
CREATE (a12)-[:WROTE]->(b12)

CREATE (b13:Book {title: 'Waves of Time', year: 2018, pages: 360})
CREATE (b13)-[:BELONGS_TO]->(g5)
CREATE (a13)-[:WROTE]->(b13)

CREATE (b14:Book {title: 'The Red Labyrinth', year: 2019, pages: 540})
CREATE (b14)-[:BELONGS_TO]->(g6)
CREATE (a14)-[:WROTE]->(b14)

CREATE (b15:Book {title: 'Echoes Within', year: 2016, pages: 290})
CREATE (b15)-[:BELONGS_TO]->(g1)
CREATE (a15)-[:WROTE]->(b15)

CREATE (b16:Book {title: 'Storm Chaser', year: 2017, pages: 370})
CREATE (b16)-[:BELONGS_TO]->(g8)
CREATE (a16)-[:WROTE]->(b16)

CREATE (b17:Book {title: 'The Memory Paradox', year: 2021, pages: 428})
CREATE (b17)-[:BELONGS_TO]->(g2)
CREATE (a17)-[:WROTE]->(b17)

CREATE (b18:Book {title: 'Beyond the Horizon', year: 2015, pages: 344})
CREATE (b18)-[:BELONGS_TO]->(g8)
CREATE (a18)-[:WROTE]->(b18)

CREATE (b19:Book {title: 'Silent Footsteps', year: 2018, pages: 305})
CREATE (b19)-[:BELONGS_TO]->(g3)
CREATE (a19)-[:WROTE]->(b19)

CREATE (b20:Book {title: 'Lost in Algorithms', year: 2020, pages: 298})
CREATE (b20)-[:BELONGS_TO]->(g4)
CREATE (a20)-[:WROTE]->(b20)

CREATE (b21:Book {title: 'Desert Flames', year: 2016, pages: 332})
CREATE (b21)-[:BELONGS_TO]->(g8)
CREATE (a21)-[:WROTE]->(b21)

CREATE (b22:Book {title: 'The Blooming Night', year: 2019, pages: 412})
CREATE (b22)-[:BELONGS_TO]->(g5)
CREATE (a22)-[:WROTE]->(b22)

CREATE (b23:Book {title: 'Parallel Realms', year: 2021, pages: 601})
CREATE (b23)-[:BELONGS_TO]->(g6)
CREATE (a23)-[:WROTE]->(b23)

CREATE (b24:Book {title: 'The Deep Code', year: 2022, pages: 275})
CREATE (b24)-[:BELONGS_TO]->(g4)
CREATE (a24)-[:WROTE]->(b24)

CREATE (b25:Book {title: 'Shadow of the Crown', year: 2020, pages: 455})
CREATE (b25)-[:BELONGS_TO]->(g7)
CREATE (a25)-[:WROTE]->(b25)

CREATE (b26:Book {title: 'The Glass Circle', year: 2014, pages: 310})
CREATE (b26)-[:BELONGS_TO]->(g1)
CREATE (a26)-[:WROTE]->(b26)

CREATE (b27:Book {title: 'Reborn Skies', year: 2017, pages: 389})
CREATE (b27)-[:BELONGS_TO]->(g2)
CREATE (a27)-[:WROTE]->(b27)

CREATE (b28:Book {title: 'Blackwater', year: 2023, pages: 320})
CREATE (b28)-[:BELONGS_TO]->(g3)
CREATE (a28)-[:WROTE]->(b28)

CREATE (b29:Book {title: 'Golden Strings', year: 2021, pages: 345})
CREATE (b29)-[:BELONGS_TO]->(g5)
CREATE (a29)-[:WROTE]->(b29)

CREATE (b30:Book {title: 'Children of the Storm', year: 2018, pages: 402})
CREATE (b30)-[:BELONGS_TO]->(g8)
CREATE (a30)-[:WROTE]->(b30)

CREATE (b31:Book {title: 'The Ancient Path', year: 2015, pages: 372})
CREATE (b31)-[:BELONGS_TO]->(g7)
CREATE (a31)-[:WROTE]->(b31)

CREATE (b32:Book {title: 'Infinite Pulse', year: 2022, pages: 488})
CREATE (b32)-[:BELONGS_TO]->(g2)
CREATE (a32)-[:WROTE]->(b32)

CREATE (b33:Book {title: 'The Hidden Gate', year: 2016, pages: 530})
CREATE (b33)-[:BELONGS_TO]->(g6)
CREATE (a33)-[:WROTE]->(b33)

CREATE (b34:Book {title: 'Mind Over Circuits', year: 2019, pages: 260})
CREATE (b34)-[:BELONGS_TO]->(g4)
CREATE (a34)-[:WROTE]->(b34)

CREATE (b35:Book {title: 'Blossoms of Dust', year: 2023, pages: 355})
CREATE (b35)-[:BELONGS_TO]->(g1)
CREATE (a35)-[:WROTE]->(b35)

CREATE (b36:Book {title: 'Marked Shadows', year: 2017, pages: 298})
CREATE (b36)-[:BELONGS_TO]->(g3)
CREATE (a36)-[:WROTE]->(b36)

CREATE (b37:Book {title: 'Love Beyond Walls', year: 2015, pages: 387})
CREATE (b37)-[:BELONGS_TO]->(g5)
CREATE (a37)-[:WROTE]->(b37)

CREATE (b38:Book {title: 'Empire of Snow', year: 2020, pages: 590})
CREATE (b38)-[:BELONGS_TO]->(g6)
CREATE (a38)-[:WROTE]->(b38)

CREATE (b39:Book {title: 'Rivertown Tales', year: 2016, pages: 310})
CREATE (b39)-[:BELONGS_TO]->(g1)
CREATE (a39)-[:WROTE]->(b39)

CREATE (b40:Book {title: 'The Final Dawn', year: 2018, pages: 450})
CREATE (b40)-[:BELONGS_TO]->(g2)
CREATE (a40)-[:WROTE]->(b40)

CREATE (b41:Book {title: 'Flowers of Damascus', year: 2021, pages: 340})
CREATE (b41)-[:BELONGS_TO]->(g7)
CREATE (a41)-[:WROTE]->(b41)

CREATE (b42:Book {title: 'Climbing the Edge', year: 2019, pages: 365})
CREATE (b42)-[:BELONGS_TO]->(g8)
CREATE (a14)-[:WROTE]->(b42)

CREATE (b43:Book {title: 'Encrypted Lives', year: 2020, pages: 289})
CREATE (b43)-[:BELONGS_TO]->(g4)
CREATE (a42)-[:WROTE]->(b43)

CREATE (b44:Book {title: 'The Pearl Line', year: 2022, pages: 330})
CREATE (b44)-[:BELONGS_TO]->(g5)
CREATE (a14)-[:WROTE]->(b44)

CREATE (b45:Book {title: 'Oath of Fire', year: 2023, pages: 612})
CREATE (b45)-[:BELONGS_TO]->(g6)
CREATE (a43)-[:WROTE]->(b45)

CREATE (b46:Book {title: 'The Lost Archive', year: 2018, pages: 310})
CREATE (b46)-[:BELONGS_TO]->(g3)
CREATE (a44)-[:WROTE]->(b46)

CREATE (b47:Book {title: 'Falling Embers', year: 2017, pages: 295})
CREATE (b47)-[:BELONGS_TO]->(g1)
CREATE (a45)-[:WROTE]->(b47)

CREATE (b48:Book {title: 'Breaking Infinity', year: 2021, pages: 476})
CREATE (b48)-[:BELONGS_TO]->(g2)
CREATE (a46)-[:WROTE]->(b48)

CREATE (b49:Book {title: 'Secrets of the Horizon', year: 2014, pages: 420})
CREATE (b49)-[:BELONGS_TO]->(g7)
CREATE (a47)-[:WROTE]->(b49)

CREATE (b50:Book {title: 'The Shadow Voyager', year: 2023, pages: 398})
CREATE (b50)-[:BELONGS_TO]->(g8)
CREATE (a48)-[:WROTE]->(b50);

// Note: Embeddings are populated by the Python application (graph.py) upon startup.
