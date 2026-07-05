<%*
const project = await tp.system.suggester(
  ["Example Project", "Reusable Workflow"],
  ["example-project", "reusable-workflow"]
);
const slug = await tp.system.prompt("slug");
const date = tp.date.now("YYYY-MM-DD");
const targetDir = project === "reusable-workflow"
  ? "raw/workflows/reusable-workflow/examples"
  : `raw/projects/${project}/examples`;
const target = `${targetDir}/${slug}-${date}`;
tR += target;
%>
