$(function () {

    $messages = $('#messages')
    $star = $("")
    userId = $("#user-id").text()

    $messages.on("click", '.fa-star', async function (e) {
        e.preventDefault()
        await updateStar($(e.target), e.target.id)
    })

    $("body").on("click", '.follow', async function (e) {
        console.log(e, e.target)
        e.preventDefault()
        
        await updateFollowing($(e.target))
    })

    async function updateFollowing($target) {
        post_url = $target.parent().attr("action")
        console.log("in updateFollowing");
        let resp = await axios.post(post_url)
        if (resp.data.dbupdate) {
            $target.toggleClass("btn-outline-primary btn-primary")
            await updateFollowingCount()
        }
    }

    async function updateFollowingCount() {
        let resp = await axios.get(`/users/${userId}/following_count`)
        $('#following').text(resp.data.count)
    }

    async function updateStar($target, id) {
        let resp = await axios.post(`/messages/${id}/like`)
        if (resp.data.dbupdate) {
            $target.toggleClass("far fas")
            await updateLikesCount()
            $('#likes').text()
        }
    }

    async function updateLikesCount() {
        let resp = await axios.get(`/users/${userId}/likes_count`)
        $('#likes').text(resp.data.count)
    }


})