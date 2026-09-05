const API_BASE = "http://127.0.0.1:8000";

async function throwBackendError(response: Response): Promise<never> {
  let detail = `Backend error: ${response.status}`;

  try {
    const payload = await response.json() as {
      detail?: string;
    };

    if (payload.detail) {
      detail = payload.detail;
    }
  } catch {
    // Keep the status-based error when the backend did not return JSON.
  }

  throw new Error(detail);
}

export async function ingestProduct(
  url: string,
  image: File,
) {
  const formData = new FormData();
  formData.append("url", url);
  formData.append("image", image);

  const response = await fetch(
    `${API_BASE}/merchant/ingest`,
    {
      method: "POST",
      body: formData,
    },
  );

  if (!response.ok) {
    await throwBackendError(response);
  }

  return response.json();
}

export async function generatePrompts(merchantId: number) {
  const response = await fetch(
    `${API_BASE}/prompts/generate`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        merchant_id: merchantId,
      }),
    },
  );

  if (!response.ok) {
    await throwBackendError(response);
  }

  return response.json();
}

export async function runSimulation(merchantId: number) {
  const response = await fetch(
    `${API_BASE}/simulation/run`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        merchant_id: merchantId,
      }),
    },
  );

  if (!response.ok) {
    await throwBackendError(response);
  }

  return response.json();
}

export async function getAudit(merchantId: number) {
  const response = await fetch(
    `${API_BASE}/audit/${merchantId}`,
  );

  if (!response.ok) {
    await throwBackendError(response);
  }

  return response.json();
}

export async function getScore(merchantId: number) {
  const response = await fetch(
    `${API_BASE}/score/${merchantId}`,
    {
      method: "POST",
    },
  );

  if (!response.ok) {
    await throwBackendError(response);
  }

  return response.json();
}
