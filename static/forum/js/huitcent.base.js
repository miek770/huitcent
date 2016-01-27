/* Scripts du template base.html de huitcent.homeip.net */

onerror=handleErr;

function handleErr(msg,url,l)
{
    var txt = "";
    txt = "Une erreur est survenue sur cette page.\n\n";
    txt += "Erreur : " + msg + "\n";
    txt += "Adresse : " + url + "\n";
    txt += "Ligne : " + l + "\n\n";
    txt += "Merci d'en informer l'administrateur du site.";
    alert(txt);
    return true;
}

function validate_todo()
{
    var description = document.forms["todo_form"]["todo_description"].value;
    if (description == null || description == "") return false;
    else return true;
}

function new_todo()
{
    if (validate_todo())
    {
        data = $('#todo_form').serializeObject();
        Dajaxice.forum.new_todo(Dajax.process, {'form': data});
        document.getElementById("todo_description").value = "";
    }
    return false;
}

function check_todo(el)
{
    Dajaxice.forum.check_todo(Dajax.process, {'id': el.id,
                                              'value': el.checked});
    return true;
}

function flush_todo()
{
    //var ans = confirm("Voulez-vous vraiment supprimer toutes les tâches complétées?");
    var ans = true;
    if (ans)
    {
        Dajaxice.forum.flush_todo(Dajax.process);
        return true;
    }
    else return false;
}

function toggle_todo()
{
    if (todo_list_visible)
    {
        document.getElementById("todo_list").style.visibility = 'hidden';
        document.getElementById("todo_menu").style.height = '14px';
        document.getElementById("toggle_todo").innerHTML = '<img src="/static/show.gif" alt="+" />';
        todo_list_visible = false;
    }
    else
    {
        document.getElementById("todo_list").style.visibility = 'visible';
        document.getElementById("todo_menu").style.height = 'auto';
        document.getElementById("toggle_todo").innerHTML = '<img src="/static/hide.gif" alt="-" />';
        todo_list_visible = true;
    }
    Dajaxice.forum.set_visibility(Dajax.process, {'item': 'show_todo',
                                                  'show': todo_list_visible});
    return true;
}

function toggle_admin()
{
    if (admin_visible)
    {
        document.getElementById("admin_list").style.visibility = 'hidden';
        document.getElementById("admin_menu").style.height = '14px';
        document.getElementById("toggle_admin").innerHTML = '<img src="/static/show.gif" alt="+" />';
        admin_visible = false;
    }
    else
    {
        document.getElementById("admin_list").style.visibility = 'visible';
        document.getElementById("admin_menu").style.height = 'auto';
        document.getElementById("toggle_admin").innerHTML = '<img src="/static/hide.gif" alt="-" />';
        admin_visible = true;
    }
    Dajaxice.forum.set_visibility(Dajax.process, {'item': 'show_admin',
                                                  'show': admin_visible});
    return true;
}
