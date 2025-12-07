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

// 2. Create Sample Data (Run as a single block)

// Create Genres
CREATE (g1:Genre {name: 'Romance'})
CREATE (g2:Genre {name: 'Science Fiction'})
CREATE (g3:Genre {name: 'Adventure'})
CREATE (g4:Genre {name: 'Thriller'})
CREATE (g5:Genre {name: 'Historical'})

// Create Authors
CREATE (a1:Author {name: 'Sara Collins'})
CREATE (a2:Author {name: 'Leo Harding'})
CREATE (a3:Author {name: 'Samira Haddad'})
CREATE (a4:Author {name: 'Julian Ross'})
CREATE (a5:Author {name: 'Chris Nolan'})

// Create Books and Relationships
CREATE (b1:Book {title: 'Ocean Whispers', year: 2017, pages: 350})
CREATE (b1)-[:BELONGS_TO]->(g1)
CREATE (a1)-[:WROTE]->(b1)

CREATE (b2:Book {title: 'Waves of Time', year: 2018, pages: 360})
CREATE (b2)-[:BELONGS_TO]->(g1)
CREATE (a1)-[:WROTE]->(b2)

CREATE (b3:Book {title: 'Storm Chaser', year: 2017, pages: 370})
CREATE (b3)-[:BELONGS_TO]->(g3)
CREATE (a2)-[:WROTE]->(b3)

CREATE (b4:Book {title: 'Love Beyond Walls', year: 2015, pages: 387})
CREATE (b4)-[:BELONGS_TO]->(g1)
CREATE (a3)-[:WROTE]->(b4)

CREATE (b5:Book {title: 'Children of the Storm', year: 2018, pages: 402})
CREATE (b5)-[:BELONGS_TO]->(g3)
CREATE (a4)-[:WROTE]->(b5)

CREATE (b6:Book {title: 'Edge of Tomorrow', year: 2020, pages: 412})
CREATE (b6)-[:BELONGS_TO]->(g2)
CREATE (a5)-[:WROTE]->(b6)

// Note: Embeddings are populated by the Python application (graph.py) upon startup.
