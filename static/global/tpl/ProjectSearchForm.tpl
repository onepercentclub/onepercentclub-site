<h2>Search Projects</h2>

<form action="/projects/search" class="ajax" method="get">
	<input name="text" type="text" />
	<select name="country__contains">
		<option value="">All countries</option>
		<option value="KE">Kenya</option>
		<option value="UG">Uganda</option>
	</select>

	<h3>Phases</h3>
	<input type="checkbox" id="cb_idea" name="phase[]" value="idea" />
	<label for="cb_idea">
		Idea
	</label><br/>
	<input type="checkbox" id="cb_plan" name="phase[]" value="plan" />
	<label for="cb_plan">
		Plan
	</label><br />
		<input type="checkbox" id="cb_act" name="phase[]" value="act" />
	<label for="cb_act">
		Fund
	</label><br />
	<input type="checkbox" id="cb_results" name="phase[]" value="results" />
	<label for="cb_results">
		Results
	</label><br />
	
	<input type="submit" value="Search" />
</form>