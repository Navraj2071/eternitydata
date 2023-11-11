console.log("Content script is running...");
chrome.runtime.onMessage.addListener(function (message, sender, sendResponse) {
  switch (message.type) {
    case "command":
      getReviews();
      sendResponse("extraction started...");
      break;
  }
});

const getReviews = async () => {
  let companyName = await getCompanyName();
  await clickReviewsButton();
  await wait(5000);
  await scrollToLastReview(20);
  let reviews = extractAllReviews();
  let data = { name: companyName, reviews: reviews };
  console.log(data);
  return data;
};

const extractAllReviews = () => {
  let allReviews = [];
  let allReviewsElements = document.getElementsByClassName("GHT2ce");
  for (i = 0; i < allReviewsElements.length; i++) {
    allReviewsElements[i].style.backgroundColor = "green";
    let review = extractReview(allReviewsElements[i]);
    let rating = extractRating(allReviewsElements[i]);
    if (rating > 0 || review !== "")
      [allReviews.push({ rating: rating, review: review })];
  }
  return allReviews;
};

const extractReview = (mainElement) => {
  let review = "";
  try {
    let reviewContainer = mainElement.getElementsByClassName("MyEned");
    let targetElement = reviewContainer[0].getElementsByClassName("wiI7pd");
    let thisReview = getInnerText(targetElement);
    console.log("review => ", thisReview);
    if (thisReview !== "") {
      review = thisReview;
    }
  } catch {}

  return review;
};
const extractRating = (mainElement) => {
  let ratingElements = mainElement.getElementsByClassName("DU9Pgb");
  let rating = 0;

  try {
    let ratingsContainer = ratingElements[0].getElementsByClassName("kvMYJc");
    let ratings = ratingsContainer[0].getElementsByTagName("img");
    for (i = 0; i <= ratings.length; i++) {
      if (
        ratings[i].src ===
        "https://maps.gstatic.com/consumer/images/icons/2x/ic_star_rate_14.png"
      ) {
        rating = rating + 1;
      }
    }
  } catch {}

  console.log("rating => ", rating);
  return rating;
};

const scrollToLastReview = async (scrolls) => {
  return new Promise(async (resolve, reject) => {
    for (i = 0; i < scrolls; i++) {
      let reviewElements = document.getElementsByClassName("GHT2ce");
      let lastElement = reviewElements[reviewElements.length - 1];
      lastElement.scrollIntoView();
      await wait(5000);
    }
    resolve();
  });
};

const clickReviewsButton = async () => {
  let buttons = document.getElementsByClassName("hh2c6");
  return new Promise((resolve, reject) => {
    for (i = 0; i < buttons.length; i++) {
      for (const child of buttons[i].children) {
        let innerText = getInnerText(child);
        if (innerText === "Reviews") {
          child.click();
          resolve();
        } else {
          for (const chil of child.children) {
            let innerText = getInnerText(chil);
            if (innerText === "Reviews") {
              child.click();
              resolve();
            }
          }
        }
      }
    }
  });
};

const getCompanyName = async () => {
  return new Promise((resolve, reject) => {
    let companyNameElement = document.getElementsByTagName("h1");
    if (companyNameElement.length > 0) {
      for (i = 0; i < companyNameElement.length; i++) {
        let element = companyNameElement[i];
        let newname = getInnerText(element);

        if (newname !== "") {
          resolve(newname);
        }
      }
    }
  });
};

const getInnerText = (element) => {
  try {
    let consideredElement = element.length > 0 ? element[0] : element;
    consideredElement.style.backgroundColor = "red";
    var plainText =
      consideredElement.textContent || consideredElement.innerText;
    return plainText;
  } catch {
    return "";
  }
};

const wait = async (time) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      resolve();
    }, time);
  });
};
