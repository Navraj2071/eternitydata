window.addEventListener("message", (e) => {
  console.log(e);
  if (e.data.from === "Bit-wallet-content-script") {
    let message = e.data.message;
    let data = e.data.data;
    if (message === "checkAccountCreated" && data.status) {
      createProvider(data);
    }
  }
});
