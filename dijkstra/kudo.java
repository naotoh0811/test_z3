package dijkstra;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.PriorityQueue;
import java.util.Queue;

/**
 *　ダイクストラ法による最短経路探索クラス
 */
public class Dijkstra {
	static final int INF = Integer.MAX_VALUE;
	private int[][] adj;
	private List<Edge>[] edges;

	/**
	 * @param adj
	 */
	@SuppressWarnings("unchecked")
	public Dijkstra(int[][] adj) {
		this.adj = adj;
		int n = calcNumOfNode(); // 頂点数
		this.edges = new List[n];

		// 隣接リスト
		for (int i = 0; i < n; i++) {
			this.edges[i] = new ArrayList<Edge>();
		}

		// ノード間を双方向接続
		for (int i = 0; i < adj.length; i++) {
			this.edges[adj[i][0]].add(new Edge(adj[i][0], adj[i][1], adj[i][2]));
			this.edges[adj[i][1]].add(new Edge(adj[i][1], adj[i][0], adj[i][2]));
		}
	}

	/**
	 * @param src
	 * @param dst
	 * @return
	 * @throws RuntimeException
	 */
	public List<Integer> getShortestPath(int src, int dst) throws RuntimeException {
		int n = calcNumOfNode(); // 頂点数

		List<Integer> paths = new ArrayList<Integer>();
		if (!dijkstra(n, src, dst, paths)) {
			throw new RuntimeException("path is none.");
		}
		System.out.println(Arrays.deepToString(paths.toArray())); // 経路
		System.out.println("hop: " + (paths.size() - 1));
		return paths;
	}

	// ダイクストラ法[単一始点最短経路(Single Source Shortest Path)]
	/**
	 * @param n
	 * @param src
	 * @param dst
	 * @param paths
	 * @return
	 */
	public boolean dijkstra(int n, int src, int dst, List<Integer> paths) {
		int[] distance = new int[n]; // 始点からの最短距離
		int[] parent = new int[n]; // 接続元ノード

		Arrays.fill(distance, INF); // 各頂点までの距離を初期化(INF 値)
		distance[src] = 0; // 始点の距離は０
		Arrays.fill(parent, -1); // -1 は始点または未到達

		Queue<Edge> q = new PriorityQueue<Edge>();
		q.add(new Edge(src, src, 0)); // 始点を入れる

		while (!q.isEmpty()) {
			Edge e = q.poll(); // 最小距離(cost)の頂点を取り出す
			if (distance[e.target] < e.cost) {
				continue;
			}

			// 隣接している頂点の最短距離を更新する
			for (Edge v : this.edges[e.target]) {
				if (distance[v.target] > distance[e.target] + v.cost) { // (始点～)接続元＋接続先までの距離
					distance[v.target] = distance[e.target] + v.cost; // 現在記録されている距離より小さければ更新
					q.add(new Edge(e.target, v.target, distance[v.target])); // 始点～接続先までの距離
					parent[v.target] = e.target; // 接続元を格納
				}
			}
		}

		// 最短経路の格納
		paths.clear();
		if (parent[dst] > -1) {
			int p = dst;
			while (p > -1) {
				paths.add(p);
				p = parent[p];
			}
			Collections.reverse(paths);
			paths.remove(0);
			paths.add(0, src);
		}
		Optional<List<Integer>> ret = Optional.ofNullable(paths);
		return distance[dst] != INF;
	}

	public int calcNumOfNode() {
		HashSet<Integer> nodes = new HashSet<>();
		for (int i = 0; i < adj.length; i++) {
			nodes.addAll(new ArrayList<Integer>(Arrays.asList(adj[i][0], adj[i][1])));
		}
		return nodes.size();
	}

	/**
	 * 辺情報の構造体
	 */
	private class Edge implements Comparable<Edge> {
		public int source = 0;
		public int target = 0;
		public int cost = 0;

		public Edge(int source, int target, int cost) {
			this.source = source;
			this.target = target;
			this.cost = cost;
		}

		@Override
		public int compareTo(Edge o) {
			return this.cost - o.cost; // コスト昇順
		}

		@Override
		public String toString() { // デバッグ用
			return "source = " + source + ", target = " + target + ", cost = " + cost;
		}
	}

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		int[][] adj = new int[][] {
				// ノード対とコスト
				{ 0, 1, 7 }, { 0, 2, 9 }, { 0, 5, 14 }, { 1, 2, 10 }, { 1, 3, 15 }, { 2, 3, 11 }, { 2, 5, 2 },
				{ 3, 4, 6 }, { 4, 5, 9 } };
		Dijkstra dijk = new Dijkstra(adj);
		dijk.getShortestPath(0, 4);
	}
}