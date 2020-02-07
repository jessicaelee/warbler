$(function () {

    $messages = $('#messages')
    $star = $("")

    $messages.on("click", '.fa-star', async function (e) {
        e.preventDefault()
        await updateStar($(e.target), e.target.id)
    })


    async function updateStar($target, id) {
        let resp = await axios.post(`/messages/${id}/like`)
        if (resp.data.dbupdate) {
            $target.toggleClass("far fas")
        }
    }
})