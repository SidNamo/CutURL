document.addEventListener("DOMContentLoaded", function () {
    const domain = 'https://cut.k-dev.me/';

    window.cutURL = async function () {
        const urlInput = document.getElementById("inputUrl");
        const url = urlInput.value.trim();
        if (!url) return;

        const response = await fetch("/cut", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ url })
        });

        if (response.ok) {
            urlInput.value = "";
            await refreshList();
        } else {
            alert("URL 단축에 실패했습니다.");
        }
    };

    window.deleteURL = async function (uid) {
        const response = await fetch("/delete", {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ uid: uid })
        });

        if (response.ok) {
            await refreshList();
        } else {
            const error = await response.json();
            alert("삭제 실패: " + error.detail);
        }
    };


    window.copyToClipboard = function (short_key) {
        navigator.clipboard.writeText(domain + short_key)
            .then(() => alert("복사되었습니다."))
            .catch(err => alert("복사 실패: " + err));
    };

    async function refreshList() {
        const response = await fetch(window.location.href);
        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, "text/html");
        const newTable = doc.querySelector("#recentTable");
        const currentTable = document.querySelector("#recentTable");
        if (newTable && currentTable) {
            currentTable.innerHTML = newTable.innerHTML;
        }
    }

    // 페이지 로딩 시 초기 목록 갱신
    refreshList();
});

