from .node import Node
import numpy as np
import random
import asyncio


class Graph:
    ID = -1

    def __init__(
        self, nodes: list[Node], adjacency_list: dict[int, list[Node]], num_DC: int
    ) -> None:
        self.nodes = nodes
        self.adjacency_list = adjacency_list
        self.num_DC = num_DC
        self._interDC_matrix = None
        self._assign_ids()
        self._init_ranks()
        self._reset_interDC_matrix()
        self.node_map = self._build_nodemap()

    def _build_nodemap(self):
        return {n.id: n for n in self.nodes}

    def _reset_interDC_matrix(self):
        self._interDC_matrix = [
            [[0, []] for _ in range(self.num_DC)] for _ in range(self.num_DC)
        ]

    def _reset_temprank(self):
        for n in self.nodes:
            n.temp_rank = 0

    def _init_ranks(self):
        for n in self.nodes:
            n.rank = 1 / len(self.nodes)

    def _assign_ids(self):
        for node in self.nodes:
            Graph.ID += 1
            node.id = Graph.ID

    async def pagerank(
        self,
        inter_DC=True,
        sampling_p: float = 1.0,
        importance_sampling: bool = False,
        num_iterations: int = 100,
        d: float = 0.85,
    ):
        if num_iterations <= 0 or sampling_p <= 0 or sampling_p > 1:
            raise ValueError("Invalid parameters")
        
        if not inter_DC:
            return await self._pgr(num_iterations, d)
        else:
            return await self._pgrdc(num_iterations, d,sampling_p,importance_sampling)

    async def _pgr(self, num_iterations: int, d: float) -> np.array:
        """pagerank implementation given all nodes are stored in one DC.

        :param int num_iterations: Number of iterations to perform
        :param float d: Damping factor
        :return np.array: Node ranks in the end
        """
        num_nodes = len(self.nodes)
        ranks = np.ones(num_nodes) / num_nodes
        adjacency_matrix = np.zeros((num_nodes, num_nodes))

        # Create adjacency matrix
        node_id_map = {node.id: idx for idx, node in enumerate(self.nodes)}
        for node_id, neighbors in self.adjacency_list.items():
            for neighbor in neighbors:
                adjacency_matrix[node_id_map[node_id]][node_id_map[neighbor.id]] = 1

        # Normalize adjacency matrix by row
        for i in range(num_nodes):
            if adjacency_matrix[i].sum() != 0:
                adjacency_matrix[i] /= adjacency_matrix[i].sum()

        for _ in range(num_iterations):
            new_ranks = np.zeros(num_nodes)
            for i in range(num_nodes):
                new_ranks[i] = (1 - d) / num_nodes + d * np.dot(
                    adjacency_matrix[:, i], ranks
                )
            ranks = new_ranks

        return ranks

    async def _build_rank(self, d,sampling_p, importance_sampling):
        self._reset_interDC_matrix()
        self._reset_temprank()

        num_nodes = len(self.nodes)
        rank_sum = np.sum([x.rank for x in self.nodes])

        for x in self.nodes:
            outcommings = self.adjacency_list[x.id]
            for o in outcommings:
                if o.DC != x.DC:
                    if importance_sampling:
                        X = np.random.binomial(1,p=x.rank / rank_sum)
                    else:
                        X = np.random.binomial(1,p=sampling_p)
                    
                    if X == 1:
                            self._interDC_matrix[x.DC][o.DC][0] += x.rank / len(outcommings)
                            self._interDC_matrix[x.DC][o.DC][1].append(o.id)
                else:
                    o.temp_rank += x.rank / len(outcommings)

        # send in parallel
        await asyncio.gather(
            *(self._send_interDC_data(targetDC=dc) for dc in range(self.num_DC))
        )

        for node in self.nodes:
            node.rank = (1 - d) * num_nodes + d * node.temp_rank
        

    async def _send_interDC_data(self, targetDC: int):
        time = random.randint(0, 1)
        await asyncio.sleep(time)

        for sendDC in range(self.num_DC):
            inter_data, receivers = self._interDC_matrix[sendDC][targetDC]

            # todo: add noise
            noise = 0
            inter_data += noise

            for receiver in receivers:
                self.node_map[receiver].temp_rank += inter_data / len(receivers)

    async def _pgrdc(self, num_iterations, d,sampling_p, importance_sampling) -> np.array:
        """pagerank implementation given nodes are stored in differernt DCs.

        :param num_iterations:
        :param d:
        :return: node ranks in the end
        """

        for _ in range(num_iterations):
            await self._build_rank(d,sampling_p, importance_sampling)

        temp = np.array([x.rank for x in self.nodes])

        return temp / np.sum(temp)
