interface playerNode {
	name: string,
	id: Array<number>
}

interface trieNode {
	value: string,
	data: Array<playerNode>,
	children: Array<trieNode>
}
	
class playerTrie {
	_head: trieNode;

	searchTrie(s: string): playerNode {
		return { name: "none", id: [0] };
	}

	generateTrie(): void {

	}

	constructor() {
		this._head = ({
			value: ".",
			data: [],
			children: []
		});
	}
}