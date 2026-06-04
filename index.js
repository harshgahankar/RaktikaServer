const express = require('express');
const cors = require('cors');
const { AccessToken } = require('livekit-server-sdk');

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 3000;
const LIVEKIT_API_KEY = process.env.LIVEKIT_API_KEY;
const LIVEKIT_API_SECRET = process.env.LIVEKIT_API_SECRET;

app.post('/getLiveKitToken', async (req, res) => {
  const { room, identity, name, metadata } = req.body ?? {};

  if (!room || !identity) {
    return res.status(400).json({ error: 'room and identity are required' });
  }

  if (!LIVEKIT_API_KEY || !LIVEKIT_API_SECRET) {
    console.error('LIVEKIT_API_KEY or LIVEKIT_API_SECRET not set');
    return res.status(500).json({ error: 'Server configuration error' });
  }

  try {
    const token = new AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET, {
      identity,
      name: name || identity,
      metadata: metadata || '',
    });
    token.addGrant({ roomJoin: true, room });

    res.json({ token: await token.toJwt() });
  } catch (err) {
    console.error('Token generation error:', err);
    res.status(500).json({ error: 'Failed to generate token' });
  }
});

app.listen(PORT, () => {
  console.log(`LiveKit token server running on port ${PORT}`);
});
