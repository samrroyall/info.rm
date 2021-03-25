const showMoreStats = () => {
    $("i.bi-plus-circle-fill").click( e => {
        const currentContainer = e.currentTarget.parentNode.parentNode;
        const currentKey = parseInt(currentContainer.attributes.key.value);
        const divId = currentContainer.parentNode.id;
        const inputs = document.getElementById(divId).getElementsByClassName("statsInputs");
        // show or hide extra stat select or filter inputs 
        for (let input of inputs) {
            if (input.attributes.key.value !== `${currentKey+1}`) continue;
            if (input.classList.contains("hide")) input.classList.remove("hide");
            else input.classList.add("hide");
        }
    });
}

const showBetweenSecondValue = key => {
    $(`select[name='filterStat${key}-logicalOp']`).change( e => {
        const logicalOp = e.currentTarget;
        const secondVal = $(`input[name='filterStat${key}-secondVal']`).first();
        // show or hide extra value for between
        if (logicalOp.value === "><") secondVal.removeClass("hide");
        else secondVal.addClass("hide");
    });
}

$(document).ready( () => {
    showMoreStats();
});