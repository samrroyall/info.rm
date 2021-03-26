function changePerNinety(isChecked) {
    const token = $("form#perNinetyForm input[name='csrfmiddlewaretoken']").first().val();
    $.ajax({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", token);
            }
        },
        method: "POST",
        url: "/change_per_ninety",
        data: {"per_ninety": isChecked},
        dataType: 'json',
        success: () => { window.location.reload(); },
        error: e => {
            alert(`The previous request resulted in an error.`);
            console.log(e);
            return;
        },
    });
}

$(document).ready( function () {
    $("form#seasonForm select").change( function () {
        const split_url = window.location.href.split("/");
        let new_href = "";
        if (split_url.length === 4) {
            new_href = split_url.join("/")
        } else if (split_url.length === 5 || split_url.length === 6) {
            new_href = split_url.slice(0, split_url.length-1).join("/")
        } else {
            alert("Cannot change season: unrecognized url!");
        }
        window.location.href = new_href + "/" + $(this).val();
    });
    $("nav#dashNav label.switch input").click( function () {
        const isChecked = $("nav#dashNav label.switch input:checked").length > 0;
        changePerNinety(isChecked);
    });
});