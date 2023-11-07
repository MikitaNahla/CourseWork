from neo4j import GraphDatabase
import asyncio


class FindGenreAgent:
    def __init__(self, genre, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.genre = genre

    async def find_genre_agent(self):
        with self.driver.session() as session:
            result = session.run(
                "MATCH (m:Node)-[:nrel_genre]->(g:Class {name: $genre}) RETURN m.name", genre=self.genre)
            pictures = [record["m.name"] for record in result]
            print(pictures)


class AddNewKnowledgeAgent:
    def __init__(self, first_node, second_node, relation, uri, username, password):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.first_node = first_node
        self.second_node = second_node
        self.relation = relation

    def check_node_existence(self, node):
        with self.driver.session() as session:
            result = session.run(
                f"MATCH (n:{node[0]}) WHERE n.{node[1]} = '{node[2]}' RETURN COUNT(n)")
            count = result.single()[0]
            return count == 0

    def check_relation_existence(self):
        with self.driver.session() as session:
            result = session.run(
                f"MATCH (n1:{self.first_node[0]})-[r:{self.relation}]->(n2:{self.second_node[0]})" +
                f" WHERE n1.{self.first_node[1]} = '{self.first_node[2]}' " +
                f"AND n2.{self.second_node[1]} = '{self.second_node[2]}'" +
                " RETURN COUNT(r) > 0")
            exists = result.single()[0]
            return exists

    def add_new_node(self, node):
        if self.check_node_existence(node):
            with self.driver.session() as session:
                session.run(f"CREATE (n:{node[0]}" + '{' + f"{node[1]}:'{node[2]}'"+'})')
        else:
            print('This node is already exist')

    def add_new_relation(self):
        if not self.check_relation_existence():
            with self.driver.session() as session:
                session.run(f"MATCH (n1:{self.first_node[0]}" + "{" + f"{self.first_node[1]}: '{self.first_node[2]}'" +
                            "})," +
                            f" (n2:{self.second_node[0]}" + "{" + f"{self.second_node[1]}: '{self.second_node[2]}'" +
                            "})" +
                            f"CREATE (n1)-[:{self.relation}]->(n2)"
                            )
        else:
            print("This relation between this two nodes is already exist")

    async def add_new_knowledge(self):
        sets = []
        if len(self.first_node) != 0:
            self.add_new_node(self.first_node)
            sets.append(self.first_node)
        if len(self.second_node) != 0:
            self.add_new_node(self.second_node)
            sets.append(self.second_node)
        if len(sets) == 2:
            self.add_new_relation()


async def main():
    uri = "bolt://localhost:7687"
    username = "Mikita"
    password = "12345123"
    genre = 'concept_portrait'
    first_node = ['Node', 'name', 'test_node1']
    second_node = ['Node', 'name', 'test_node2']
    relation = 'test_relation'
    agent1 = FindGenreAgent(genre, uri, username, password)
    agent2 = AddNewKnowledgeAgent(first_node, second_node, relation, uri, username, password)
    await agent1.find_genre_agent()
    await agent2.add_new_knowledge()
    print('The end of the program')


if __name__ == '__main__':
    asyncio.run(main())

