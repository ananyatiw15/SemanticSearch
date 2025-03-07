const API_URL = "http://18.219.24.230:8080/query";

async function fetchPapers(query, k = 5) {
  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, k }),
    });

    if (!response.ok) throw new Error("Failed to fetch");

    return await response.json();
  } catch (error) {
    console.error("Error fetching data:", error);
    return { results: [] };
  }
}

export default fetchPapers;
