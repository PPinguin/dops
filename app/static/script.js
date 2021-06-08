var form = null
var parent = null

window.addEventListener( "pageshow", function ( event ) {
    var historyTraversal = event.persisted || 
                           ( typeof window.performance != "undefined" && 
                                window.performance.navigation.type === 2 );
    if ( historyTraversal ) {
        // Handle page restore.
        window.location.reload();
    }
});

function answer(element){
    if (parent != $(element).parent() && form != null) close(form)
    parent = $(element).parent()
    form = parent.find(".riddle-form")
    if (!form.length){
        form = $('<div class="riddle-form" style="display:none"></div>')
            .append($('<span class="close">&#x2716;</span>').click(() => close(form)))
            .append("<input type='text' id='input'>")
        form.appendTo(parent)
            .slideDown('fast', ()=>form.find('#input').focus())
    } else if (form.find('#input').val() != "") {
        console.log({ 
            "id": parent.attr('id'), 
            "answer": form.find('#input').val() 
        });
        $.ajax({
            type: 'POST',
            data: { 
                id: parent.attr('id'), 
                answer: form.find('#input').val() 
            },
            url: '/answer',
            dataType: "json",
            cache: true,
            success: function(response){
                if (response['response']){
                    parent.css('--base', '#1fab62')
                } else {
                    parent.css('--base', '#ab1f1f')
                }
                $(element).find("p").text("Show answer")
                let n = $(element).find("span")
                n.text(+n.text()+1)
                $(element).click(() => info(element))
                close(form)
            },
            error: function(response){
                
            }
        })
    }
}

function info(element){
    if (parent != $(element).parent() && form != null) close(form)
    parent = $(element).parent()
    form = parent.find(".riddle-form")
    if (!form.length){
        form = $('<div class="riddle-form" style="display:none"></div>')
            .append($('<span class="close">&#x2716;</span>').click(() => close(form)))
        form.appendTo(parent)
        $.post('/info', {
            id: parent.attr('id')
        }).done(
            function(response){
                form.append(`
                    <p>Correct answer: ${response['correct']}</p>
                    <p>Your answer: ${response['custom']}</p>`
                ).slideDown('fast')
            }
        ).fail(
            function(response){
                form.append(`<p>No data, so strange!</p>`).slideDown('fast')
            }
        )
    }
}

function close(form){
    form.slideUp('fast', ()=>{
        form.remove()
        form = null
    })
}