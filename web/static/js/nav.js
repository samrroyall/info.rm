////////////////////////////////
//// JQUERY STYLE FUNCTIONS ////
////////////////////////////////

const toggleSecondRow = () => {
    const originalHeight = $(window).width()/100 + 25;
    const newHeight = $(window).width()/100 + 90;
    let current_display = $("nav#mainNav li.leagueNav div.secondRow").css("display");
    if (current_display === "none") {
        // show up arrow
        $("nav#mainNav li.leagueNav div.firstRow i.bi-caret-down-fill").hide();
        $("nav#mainNav li.leagueNav div.firstRow i.bi-caret-up-fill").show();
        // fade second row in
        $("nav#mainNav li.leagueNav div.secondRow").show();
        $("nav#mainNav li").animate(
            {height: `${newHeight}px`},
            1000, 
            () => $("nav li.leagueNav div.secondRow").css("display", "flex") 
        );
    } else {
        // show down arrow
        $("nav#mainNav li.leagueNav div.firstRow i.bi-caret-up-fill").hide();
        $("nav#mainNav li.leagueNav div.firstRow i.bi-caret-down-fill").show();
        // fade second row out
        $("nav#mainNav li").animate({height: `${originalHeight}px`}, 1000);
        setTimeout(() => $("nav#mainNav li.leagueNav div.secondRow").hide(), 1000);
    }
}

// show/hide collapsed navbar with burger menu
const toggleCollapsedNav = () => {
    const newHeight = 3*$(window).width()/100 + 185;
    const current_display = $("nav#collapsedNav").css("display");
    if (current_display === "none") {
        // fade collapsed nav content in  
        $("nav#collapsedNav").css("height", "0px");
        $("nav#collapsedNav").show();
        $("nav#collapsedNav").animate(
            {height: `${newHeight}px`}, 
            1000, 
            () => $("nav#collapsedNav").css("display", "flex")
        );
    } else {
        // fade collapsed nav content out
        $("nav#collapsedNav").animate({height: "0px"},  1000);
        setTimeout(() => $("nav#collapsedNav").hide(), 1000);
    }
}

//////////////////////////////////
///////// TRIE FUNCTIONS /////////
//////////////////////////////////

const searchTrie = (root, queryStr) => {
    let searchResult = new Set();

    const query = queryStr.trim().toLocaleLowerCase();
    for (let word of query.split(' ')) {
        // only count words with at least two letters
        if (word.length < 2) continue;
        // traverse trie to last node if it exists 
        let currNode = root;
        for (let letter of word) {
            if (!currNode.children.hasOwnProperty(letter)) {
                currNode = null;
                break;
            }
            currNode = currNode.children[letter];
        }

        // if there was no node matching the word,
        // continue to next word
        if (currNode == null) continue;

        // for each node in the subtree beginning at currNode
        // add its value to tempResult
        let tempResult = new Set();
        const nodeQueue = [currNode];
        while (nodeQueue.length > 0) {
            const node = nodeQueue.shift();
            // add elements of node.value to tempResult
            if (node.value !== null) {
                for (let entry of node.value) {
                    tempResult.add(entry);
                }
            }
            // add elements of node.children to nodeQueue
            for (let letter in node.children) {
                nodeQueue.push(node.children[letter]);
            }
        }

        // on first iteration, all results are valid
        if (searchResult.size === 0) {
            searchResult = tempResult;
            continue;
        }
        // set result to intersection with tempResult
        searchResult = new Set([...searchResult].filter(elem => tempResult.has(elem)));
    }

    // return first 10 results sorted by name
    return Array.from(searchResult)
        .sort((a, b) => a.name.localeCompare(b.name))
        .slice(0, 10);
    
}

const addWord = (root, word, data) => {
    let currNode = root;
    // loop through trie with word's letters
    for (let letter of word) {
        if (!currNode.children.hasOwnProperty(letter)) {
            currNode.children[letter] = { value: null, children: {} };
        }
        currNode = currNode.children[letter];
    }
    // add data to value of last node
    if (currNode.value === null) currNode.value = [];
    currNode.value.push(data);
}

const generateTrie = data => {
    // create root node
    let trie = {
        value: null,
        children: {},
    }
    // add each word from each name in data to trie
    for (let entry of data) {
        for (let word of entry.name.split(' ')) {
            addWord(trie, word, entry);
        }
    }
    return trie;
}

async function createTrie(url, token) {
    // AJAX GET request to grab player, league, or team data 
    return $.ajax({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", token);
            }
        },
        method: "GET",
        url: url,
        success: res => {
            return res;
        },
        error: errs => {
            console.log(`Request to '${url}' resulted in an error`)
            // return null on error
            return null;
        },
    });
}

const playerSearch = (tries, e) => {
    const query = e.target.value;
        
    // player search result 
    const playerResult = searchTrie(tries.players, query);
    const playerList = playerResult.map(player =>
        `<li class='entry'><a href='#'>${player.name}</a></li>`
    );
    // add teams to result
    const teamResult = searchTrie(tries.teams, query);
    const teamList = teamResult.map(team =>
        `<li class='entry'><a href='#'>${team.name}</a></li>`
    );
    // add leagues to result
    const leagueResult = searchTrie(tries.leagues, query);
    const leagueList = leagueResult.map(league =>
        `<li class='entry'><a href='#'>${league.name}</a></li>`
    );

    const resultList = (e.target.id === "mainSearchBar" ? $("ul#mainSearchResults") : $("ul#collapsedSearchResults") );
    // clear previous result list
    resultList.html("");
    // create result list
    resultList.html(`
    <li class='header'> PLAYERS </li>
    ${playerList.join('\n')}
    <li class='header'> TEAMS </li>
    ${teamList.join('\n')}
    <li class='header'> LEAGUES </li>
    ${leagueList.join('\n')}
    `);
}

//////////////////////////
///// DOCUMENT.READY /////
//////////////////////////

$(document).ready( () => {
    // autohide collapsed nav at certain window sizes
    $(window).resize( () => {
        if ( $(window).width() >= 1007 ) $("nav#collapsedNav").hide()
    });
    // toggle second row when arrow is clicked
    $("nav#mainNav li.leagueNav div.firstRow i").click( () => toggleSecondRow() );
    // toggle collapsed navbar when burger button is pressed
    $("nav#mainNav li.burgerButton i").click( () => toggleCollapsedNav() );
    // prevent default submit behavior of forms
    $("nav#mainNav form").submit( e => e.preventDefault() );
    $("nav#collapsedNav form").submit( e => e.preventDefault() );

    // create tries
    const token = $("nav#mainNav form#searchForm input[name='csrfmiddlewaretoken']").val();
    const tries = { players: [], teams: [], leagues: [] };
    createTrie('/get_players', token) 
        .then(res => tries.players = generateTrie(res.result));
    createTrie('/get_teams', token)
        .then(res => tries.teams = generateTrie(res.result));
    createTrie('/get_leagues', token)
        .then(res => tries.leagues = generateTrie(res.result));

    // as user types, return search results
    $("nav form input[type='text']").keyup( e => playerSearch(tries, e) );
});