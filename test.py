from graph import Node, Graph
import asyncio

# 示例使用
num_iter =30
num_dc = 2
nodes = [Node(DC=0), Node(DC=1), Node(DC=0)]
adjacency_list = {
    0: [nodes[1], nodes[2]],
    1: [nodes[0]],
    2: [nodes[0]]
}
graph = Graph(nodes, adjacency_list, num_dc)

async def main():
    ranks = await graph.pagerank(inter_DC=False, num_iterations=num_iter, d=0.85)
    print(ranks)
    
    ranks = await graph.pagerank(inter_DC=True, num_iterations=num_iter, d=0.85)
    print(ranks)
    
    ranks = await graph.pagerank(inter_DC=True, num_iterations=num_iter, d=0.85, sampling_p=0.8)
    print(ranks)
    
    ranks = await graph.pagerank(inter_DC=True, num_iterations=num_iter, d=0.85, importance_sampling= True)
    print(ranks)

asyncio.run(main())