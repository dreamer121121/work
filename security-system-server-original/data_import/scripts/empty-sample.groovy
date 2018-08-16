// define the default TraversalSource to bind queries to.
g1 = graph1.traversal()
g2 = graph2.traversal()
kb = knowledgeBase.traversal()

graph1.addVertex('name', 'INDEX')
graph2.addVertex('name', 'INDEX')
knowledgeBase.addVertex('name', 'INDEX')