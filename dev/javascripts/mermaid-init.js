// Initialize Mermaid for MkDocs Material theme
document$.subscribe(() => {
  mermaid.initialize({
    startOnLoad: true,
    theme: document.body.getAttribute("data-md-color-scheme") === "slate" ? "dark" : "default",
    themeVariables: {
      fontSize: "16px"
    },
    flowchart: {
      useMaxWidth: true,
      htmlLabels: true,
      curve: "basis"
    },
    sequence: {
      useMaxWidth: true,
      diagramMarginX: 50,
      diagramMarginY: 10,
      boxTextMargin: 5,
      noteMargin: 10,
      messageMargin: 35
    }
  });

  // Re-render mermaid diagrams when theme changes
  var observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.attributeName === "data-md-color-scheme") {
        location.reload();
      }
    });
  });

  observer.observe(document.body, {
    attributes: true,
    attributeFilter: ["data-md-color-scheme"]
  });
});

