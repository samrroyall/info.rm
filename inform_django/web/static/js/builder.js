const showMoreStats = () => {
    $("form#builderForm i.bi-plus-circle-fill").click( e => {
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

const showBetweenSecondValue = prefix => {
    $(`form#builderForm select[name='${prefix}-logicalOp']`).change( e => {
        const logicalOp = e.currentTarget;
        const secondVal = $(`form#builderForm input[name='${prefix}-secondVal']`).first();
        // show or hide extra value for between
        if (logicalOp.value === "><") secondVal.removeClass("hide");
        else secondVal.addClass("hide");
    });
}

const showLeagueTeams = () => {
    $("form#builderForm select[name='teamLeague']").change( e => {
        const currStartYear = $("form#builderForm select[name='season']").val();
        const currLeague = e.currentTarget.value;
        const clubs = e.currentTarget.parentElement.getElementsByTagName("select")[1].getElementsByTagName("option");
        for (let club of clubs) {
            if (
                club.classList.contains(`league-${currLeague}`) &&
                club.classList.contains(`season-${currStartYear}`)
            ) {
                club.classList.remove("hide");
                continue;
            }
            club.classList.add("hide");
        }
    });
}

const showQueryFilters = () => {
    $("form#builderForm select#queryFilterSelect").change( e => {
        const labelId = e.currentTarget.value;
        if (labelId === "") {
            const queryFilterLabels = $("div#queryFilters label");
            // clear values
            queryFilterLabels.children("select").val("");
            queryFilterLabels.children("input").val("");
            // hide inputs
            queryFilterLabels.addClass("hide");
            return;
        }
        $(`label#${labelId}`).removeClass("hide");
    });
}

const builderFormData = () => {
    return {
        season_start: $("form#builderForm select[name='season']").first().val(),
        selectStats: [
            {
                arithOp: $("form#builderForm select[name='selectStat0-arithOp']").first().val(),
                firstStat: $("form#builderForm select[name='selectStat0-firstStat']").first().val(),
                secondStat: $("form#builderForm select[name='selectStat0-secondStat']").first().val(),
                perNinety: $("form#builderForm input[name='selectStat0-perNinety']").first().is(":checked"),
            },
            {
                arithOp: $("form#builderForm select[name='selectStat1-arithOp']").first().val(),
                firstStat: $("form#builderForm select[name='selectStat1-firstStat']").first().val(),
                secondStat: $("form#builderForm select[name='selectStat1-secondStat']").first().val(),
                perNinety: $("form#builderForm input[name='selectStat1-perNinety']").first().is(":checked"),
            },
            {
                arithOp: $("form#builderForm select[name='selectStat2-arithOp']").first().val(),
                firstStat: $("form#builderForm select[name='selectStat2-firstStat']").first().val(),
                secondStat: $("form#builderForm select[name='selectStat2-secondStat']").first().val(),
                perNinety: $("form#builderForm input[name='selectStat1-perNinety']").first().is(":checked"),
            },
        ],
        league_id: $("form#builderForm select[name='league']").first().val(),
        team: {
            id: $("form#builderForm select[name='team']").first().val(),
            league_id: $("form#builderForm select[name='teamLeague']").first().val(),
        },
        age: {
            logicalOp: $("form#builderForm select[name='age-logicalOp']").first().val(),
            firstVal: $("form#builderForm input[name='age-firstVal']").first().val(),
            secondVal: $("form#builderForm input[name='age-secondVal']").first().val(),
        },
        minutesPlayed: {
            logicalOp: $("form#builderForm select[name='minutesPlayed-logicalOp']").first().val(),
            firstVal: $("form#builderForm input[name='minutesPlayed-firstVal']").first().val(),
            secondVal: $("form#builderForm input[name='minutesPlayed-secondVal']").first().val(),
        },
        filterStats: [
            {
                arithOp: $("form#builderForm select[name='filterStat0-arithOp']").first().val(),
                firstStat: $("form#builderForm select[name='filterStat0-firstStat']").first().val(),
                secondStat: $("form#builderForm select[name='filterStat0-secondStat']").first().val(),
                perNinety: $("form#builderForm input[name='filterStat0-perNinety']").first().is(":checked"),
                logicalOp: $("form#builderForm select[name='filterStat0-logicalOp']").first().val(),
                firstVal: $("form#builderForm input[name='filterStat0-firstVal']").first().val(),
                secondVal: $("form#builderForm input[name='filterStat0-secondVal']").first().val(),
            },               
            {
                arithOp: $("form#builderForm select[name='filterStat1-arithOp']").first().val(),
                firstStat: $("form#builderForm select[name='filterStat1-firstStat']").first().val(),
                secondStat: $("form#builderForm select[name='filterStat1-secondStat']").first().val(),
                perNinety: $("form#builderForm input[name='filterStat1-perNinety']").first().is(":checked"),
                logicalOp: $("form#builderForm select[name='filterStat1-logicalOp']").first().val(),
                firstVal: $("form#builderForm input[name='filterStat1-firstVal']").first().val(),
                secondVal: $("form#builderForm input[name='filterStat1-secondVal']").first().val(),
            },
            {
                arithOp: $("form#builderForm select[name='filterStat2-arithOp']").first().val(),
                firstStat: $("form#builderForm select[name='filterStat2-firstStat']").first().val(),
                secondStat: $("form#builderForm select[name='filterStat2-secondStat']").first().val(),
                perNinety: $("form#builderForm input[name='filterStat2-perNinety']").first().is(":checked"),
                logicalOp: $("form#builderForm select[name='filterStat2-logicalOp']").first().val(),
                firstVal: $("form#builderForm input[name='filterStat2-firstVal']").first().val(),
                secondVal: $("form#builderForm input[name='filterStat2-secondVal']").first().val(),
            },
        ],
        country: $("form#builderForm select[name='nationality']").first().val(),
        position: $("form#builderForm select[name='position']").first().val(),
        orderBy: {
            arithOp: $("form#builderForm select[name='orderBy-arithOp']").first().val(),
            firstStat: $("form#builderForm select[name='orderBy-firstStat']").first().val(),
            secondStat: $("form#builderForm select[name='orderBy-secondStat']").first().val(),
            perNinety: $("form#builderForm input[name='orderBy-perNinety']").first().is(":checked"),
            lowToHigh: $("form#builderForm input[name='orderBy-lowToHigh']").first().is(":checked"),
        },
    }
}

const displayErrors = errors => {
    console.log(errors);
    // clear old errors
    $('form#builderForm div.errors').html("");
    for (const [id, errs] of Object.entries(errors)) {
        // display new errors
        $(`div#${id}`).html("<ul>" + errs.map(err => `<li>${err}</li>`).join("") + "</ul>");
    }
}

const builderFormSubmit = () => {
    $("form#builderForm").submit( e => {
        e.preventDefault();
        const formData = builderFormData();
        const token = $("form#builderForm input[name='csrfmiddlewaretoken']").first().val();
        $.ajax({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", token);
                }
            },
            method: "POST",
            url: "/make_query",
            data: JSON.stringify(formData),
            dataType: 'json',
            success: res => { console.log(res); },
            error: errs => { displayErrors(errs.responseJSON); },
        });
    });
}

$(document).ready( () => {
    showMoreStats();
    showLeagueTeams();
    for (let key = 0; key < 3; key++) showBetweenSecondValue(`filterStat${key}`);
    showBetweenSecondValue("age");
    showBetweenSecondValue("minutesPlayed");
    showQueryFilters();
    builderFormSubmit();
});