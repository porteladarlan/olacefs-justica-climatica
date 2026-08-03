(() => {
    const form = document.querySelector("[data-tools-filter-form]");
    const search = form?.querySelector("[data-tools-progressive-search]");
    if (!form || !search) return;

    let timer;
    let request;

    const updateResults = async () => {
        request?.abort();
        request = new AbortController();

        const url = new URL(window.location.pathname, window.location.origin);
        const query = search.value.trim();
        const sector = form.querySelector('input[name="setor"]')?.value;
        if (query) url.searchParams.set("q", query);
        if (sector) url.searchParams.set("setor", sector);

        const currentList = document.querySelector(".tools-list");
        currentList?.setAttribute("aria-busy", "true");
        try {
            const response = await window.fetch(url, {
                headers: { "X-Requested-With": "XMLHttpRequest" },
                signal: request.signal,
            });
            if (!response.ok) throw new Error("Falha ao atualizar o catálogo.");

            const nextDocument = new DOMParser().parseFromString(
                await response.text(),
                "text/html",
            );
            const nextList = nextDocument.querySelector(".tools-list");
            const nextCounter = nextDocument.querySelector(".tools-counter");
            const currentCounter = document.querySelector(".tools-counter");
            if (!nextList || !nextCounter || !currentCounter) {
                throw new Error("Resposta incompleta do catálogo.");
            }

            currentCounter.replaceWith(nextCounter);
            currentList.replaceWith(nextList);
            window.history.replaceState({}, "", url);
        } catch (error) {
            if (error.name !== "AbortError") form.submit();
        } finally {
            document.querySelector(".tools-list")?.removeAttribute("aria-busy");
        }
    };

    search.addEventListener("input", () => {
        window.clearTimeout(timer);
        timer = window.setTimeout(updateResults, 300);
    });
})();
