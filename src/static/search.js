let root = ({
    "value": null,
    "children": new Map()
});

function addPlayer(name, player) {
    let currNode = root;
    // traverse trie and set new children when needed
    for (let i = 0; i < name.length; i++) {
        let letter = name.charAt(i);
        if (!currNode.children.has(letter)) {
            currNode.children.set(
                letter,
                { "value": null, "children": new Map() }
            )
        }
        currNode = currNode.children.get(letter);
    }
    // set value of last node 
    if (currNode.value !== null) {
        currNode.value.push(player);
    } else {
        currNode.value = new Array();
        currNode.value.push(player);
    }
}

function searchTrie(queryString) {
    let queryResult = new Set();

    let query = queryString.trim().toLocaleLowerCase();
    let words = query.split(" ");
    for (let i = 0; i < words.length; i++) {
        let tempSet = null;
        if (i > 0) {
            tempSet = new Set();
        }

        let word = words[i];
        let strLen = word.length;
        if (strLen == 0) {
            continue;
        }
        let currNode = root;

        // traverse trie and print contents of last node
        for (let j = 0; j < strLen; j++) {
            letter = word.charAt(j);
            if (currNode.children.has(letter)) {
                currNode = currNode.children.get(letter);
            } else {
                currNode = null;
            }
        }

        // print all players in current subtree
        if (currNode !== null) {
            let queue = new Array();
            queue.push(currNode);
            while (queue.length > 0) {
                let back = queue.pop();
                if (back.value !== null) {
                    for (let val of back.value) {                       
                        if (tempSet !== null) {
                            tempSet.add(val);
                        } else {
                            queryResult.add(val);
                        }
                    }
                }
                for (let child of back.children.values()) {
                    queue.push(child);
                }
            }
        }

        // set instersection if multiple words
        if (tempSet !== null) {
            let temp = new Set([...queryResult].filter(x => tempSet.has(x)));
            queryResult = temp;
        }
    }

    // sort set
    return (
        Array.from(queryResult)
             .sort((a, b) => a.name.localeCompare(b.name))
             .slice(0, 10)
    );
}

function generateTrie(playerDict) {
    let data = $.parseJSON(playerDict);
    for (let player of data) {
        for (let word of player.name.split(" ")) {                
            addPlayer(word, player);
        }
    }
}