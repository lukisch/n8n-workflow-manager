/**
 * n8nManager API Client
 */
const apiClient = {
    async request(method, url, data = null) {
        const opts = {
            method,
            headers: {'Content-Type': 'application/json'},
        };
        if (data) opts.body = JSON.stringify(data);
        try {
            const resp = await fetch(url, opts);
            const json = await resp.json();
            if (!resp.ok) json.ok = false;
            else json.ok = true;
            return json;
        } catch(e) {
            return {ok: false, detail: e.message};
        }
    },
    get(url) { return this.request('GET', url); },
    post(url, data) { return this.request('POST', url, data); },
    put(url, data) { return this.request('PUT', url, data); },
    delete(url) { return this.request('DELETE', url); },
};
