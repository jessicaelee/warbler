$(function () {

    $messages = $('#messages')
    $star = $("")
    userId = $("#user-id").text()
    usersOwnPage = $("#logged-in-users-page").text()


    $messages.on("click", '.fa-star', async function (e) {
        e.preventDefault()
        await updateStar($(e.target), e.target.id)
    })

    $("body").on("click", '.follow-button', async function (e) {
        e.preventDefault()
        await updateFollowing($(e.target))
    })

    async function updateFollowing($target) {
        post_url = $target.parent().attr("action")
        let resp = await axios.post(post_url)
        if (resp.data.dbupdate) {
            $target.toggleClass("btn-outline-primary btn-primary")
            let id = $target.data().userid;
            if ($target.text().includes("Unfollow")) {
                $target.text("Follow")
                $target.parent().attr("action", `/users/follow/${id}`)
            } else {
                $target.text("Unfollow")
                $target.parent().attr("action", `/users/stop-following/${id}`)
            }
            if (userId) {
                await updateFollowingCount()
            }
            if (usersOwnPage !== "loggedin") {
                await updateFollowersCount()
            }

        }
    }

    async function updateFollowingCount() {
        let resp = await axios.get(`/users/${userId}/following_count`)
        $('#following').text(resp.data.count)
    }

    async function updateFollowersCount() {
        let resp = await axios.get(`/users/${userId}/followers_count`)
        $('#followers').text(resp.data.count)
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