export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { dream_text } = req.body;
  if (!dream_text) {
    return res.status(400).json({ error: 'Dream text is required' });
  }

  const apiKey = process.env.QWEN_API_KEY;
  const apiUrl = process.env.QWEN_API_URL;

  const body = {
    model: "qwen-plus",
    messages: [
      {
        role: "system",
        content: "You are a professional dream interpreter. Please analyze the user's dream in detail using psychology, culture, and symbolism, and output in Markdown format."
      },
      {
        role: "user",
        content: dream_text
      }
    ]
  };

  try {
    const apiRes = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify(body)
    });

    if (!apiRes.ok) {
      const err = await apiRes.text();
      return res.status(apiRes.status).json({ error: err });
    }

    const data = await apiRes.json();
    return res.status(200).json(data);
  } catch (error) {
    return res.status(500).json({ error: error.message || 'Internal server error' });
  }
} 