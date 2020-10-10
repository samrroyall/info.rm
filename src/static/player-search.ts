interface playerNode {
	name: string,
	id: number
}

interface trieNode {
	value: string,
	data: Array<playerNode>,
	children: Array<trieNode>
}
	
class playerTrie {
	_head: trieNode;

	searchTrie(s: string): playerNode {
		return { name: "none", id: 0 };
	}

	constructor() {
		this._head = ({
			value: ".",
			data: [],
			children: []
		});
		// query DB for player name and ID information
		let players: string = "SELECT players.firstname, players.lastname, players.id FROM players ORDER BY players.firstname;";
		// convert players to playerNodes
		// ...
		// insert playerNodes into trie
		// ...
	}
}